/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//! Query interface for pyrefly. Just experimenting for the moment - not intended for external use.

use std::io::Cursor;
use std::path::PathBuf;
use std::sync::Arc;

use dupe::Dupe;
use pyrefly_python::ast::Ast;
use pyrefly_python::module_name::ModuleName;
use pyrefly_python::module_path::ModulePath;
use pyrefly_python::sys_info::SysInfo;
use pyrefly_util::events::CategorizedEvents;
use pyrefly_util::lined_buffer::DisplayRange;
use pyrefly_util::lock::Mutex;
use pyrefly_util::prelude::SliceExt;
use pyrefly_util::prelude::VecExt;
use pyrefly_util::visit::Visit;
use ruff_python_ast::Expr;
use ruff_python_ast::ExprAttribute;
use ruff_python_ast::ModModule;
use ruff_python_ast::name::Name;
use ruff_text_size::Ranged;
use starlark_map::small_set::SmallSet;

use crate::alt::answers::Answers;
use crate::config::finder::ConfigFinder;
use crate::module::module_info::ModuleInfo;
use crate::state::handle::Handle;
use crate::state::require::Require;
use crate::state::state::State;
use crate::types::display::TypeDisplayContext;

pub struct Query {
    /// The state that we use.
    state: State,
    /// The SysInfo, the same for all handles.
    sys_info: SysInfo,
    /// The files that have been used with `add_files`, used when files change.
    files: Mutex<SmallSet<(ModuleName, ModulePath)>>,
}

impl Query {
    pub fn new(config_finder: ConfigFinder) -> Self {
        let state = State::new(config_finder);
        Self {
            state,
            sys_info: SysInfo::default(),
            files: Mutex::new(SmallSet::new()),
        }
    }

    fn make_handle(&self, name: ModuleName, path: ModulePath) -> Handle {
        Handle::new(name, path, self.sys_info.dupe())
    }

    pub fn change_files(&self, events: &CategorizedEvents) {
        let mut transaction = self
            .state
            .new_committable_transaction(Require::Everything, None);
        let new_transaction_mut = transaction.as_mut();
        new_transaction_mut.invalidate_events(events);
        new_transaction_mut.run(&[]);
        self.state.commit_transaction(transaction);
        let all_files = self.files.lock().iter().cloned().collect::<Vec<_>>();
        self.add_files(all_files);
    }

    pub fn change(&self, files: Vec<(ModuleName, std::path::PathBuf)>) {
        let modified_paths = files.into_iter().map(|(_, path)| path).collect();
        let events = CategorizedEvents {
            created: Vec::new(),
            modified: modified_paths,
            removed: Vec::new(),
            unknown: Vec::new(),
        };
        self.change_files(&events);
    }

    /// Load the given files and return any errors associated with them
    pub fn add_files(&self, files: Vec<(ModuleName, ModulePath)>) -> Vec<String> {
        self.files.lock().extend(files.clone());
        let mut transaction = self
            .state
            .new_committable_transaction(Require::Everything, None);
        let handles =
            files.into_map(|(name, file)| (self.make_handle(name, file), Require::Everything));
        transaction.as_mut().run(&handles);
        let errors = transaction
            .as_mut()
            .get_errors(handles.iter().map(|(h, _)| h));
        self.state.commit_transaction(transaction);
        errors.collect_errors().shown.map(|e| {
            // We deliberately don't have a Display for `Error`, to encourage doing the right thing.
            // But we just hack something up as this code is experimental.
            let mut s = Cursor::new(Vec::new());
            e.write_line(&mut s, false).unwrap();
            String::from_utf8_lossy(&s.into_inner()).into_owned()
        })
    }

    pub fn get_types_in_file(
        &self,
        name: ModuleName,
        path: ModulePath,
    ) -> Option<Vec<(DisplayRange, String)>> {
        let handle = self.make_handle(name, path);

        let transaction = self.state.transaction();
        let ast = transaction.get_ast(&handle)?;
        let module_info = transaction.get_module_info(&handle)?;
        let answers = transaction.get_answers(&handle)?;

        let mut res = Vec::new();
        fn f(
            x: &Expr,
            module_info: &ModuleInfo,
            answers: &Answers,
            res: &mut Vec<(DisplayRange, String)>,
        ) {
            let range = x.range();
            if let Some(ty) = answers.get_type_trace(range) {
                let mut ctx = TypeDisplayContext::new(&[&ty]);
                ctx.always_display_module_name();
                res.push((
                    module_info.display_range(range),
                    ctx.display(&ty).to_string(),
                ));
            }
            x.recurse(&mut |x| f(x, module_info, answers, res));
        }

        ast.visit(&mut |x| f(x, &module_info, &answers, &mut res));
        Some(res)
    }

    /// Given an expression, which contains qualified types, guess which imports to add.
    ///
    /// For example `foo.bar.baz` will return `[foo.bar]`.
    fn find_imports(x: &ModModule) -> Vec<String> {
        fn g(x: &ExprAttribute) -> Option<Vec<&Name>> {
            match &*x.value {
                Expr::Attribute(x) => {
                    let mut res = g(x)?;
                    res.push(&x.attr.id);
                    Some(res)
                }
                Expr::Name(x) => Some(vec![&x.id]),
                _ => None,
            }
        }

        fn f(x: &Expr, res: &mut SmallSet<String>) {
            if let Expr::Attribute(x) = x {
                if let Some(module) = g(x) {
                    res.insert(module.map(|x| x.as_str()).join("."));
                }
            } else {
                x.recurse(&mut |x| f(x, res));
            }
        }
        let mut res = SmallSet::new();
        x.visit(&mut |x| f(x, &mut res));
        res.into_iter().collect()
    }

    /// Return `Err` if you can't resolve them to types, otherwise return `lt <: gt`.
    pub fn is_subtype(
        &self,
        name: ModuleName,
        path: PathBuf,
        lt: &str,
        gt: &str,
    ) -> Result<bool, String> {
        let types = format!("type pyrefly_lt = ({lt})\ntype pyrefly_gt = ({gt})\n");
        let imported = Self::find_imports(&Ast::parse(&types).0);
        let imports = imported.map(|x| format!("import {x}\n")).join("");
        let check = "def pyrefly_func(x: pyrefly_lt) -> pyrefly_gt:\n    return x";

        let before = format!("{imports}\n{types}\n");
        let after = format!("{imports}\n{types}\n{check}");

        let mut t = self.state.transaction();
        let h = self.make_handle(name, ModulePath::memory(path.clone()));
        t.set_memory(vec![(path.clone(), Some(Arc::new(before.clone())))]);
        t.run(&[(h.dupe(), Require::Everything)]);
        let errors = t.get_errors([&h]).collect_errors();
        if !errors.shown.is_empty() {
            let mut res = Vec::new();
            for e in errors.shown {
                e.write_line(&mut Cursor::new(&mut res), true).unwrap();
            }
            return Err(format!(
                "Errors from is_subtype `{lt}` <: `{gt}`\n{}\n\nSource code:\n{before}",
                str::from_utf8(&res).unwrap_or("UTF8 error")
            ));
        }
        t.set_memory(vec![(path.clone(), Some(Arc::new(after)))]);
        t.run(&[(h.dupe(), Require::Everything)]);
        let errors = t.get_errors([&h]).collect_errors();
        Ok(errors.shown.is_empty())
    }
}
