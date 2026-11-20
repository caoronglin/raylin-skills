# raylin-skills

Merged collection of personal Claude/Agent skills. Four source repositories are preserved as subtrees, each under its own top-level directory so identical filenames (`SKILL.md`, `README.md`, ...) never collide. Original git history is retained via `git subtree`.

## Contents

| Directory | Source repository | What it holds |
|---|---|---|
| `cherry-custom-skills/` | `caoronglin/cherry-custom-skills` | Custom skills: docx report delivery, daily self-evolution review, Obsidian vault maintenance, maize GWAS/EWAS annotation, CUMCM delivery gate |
| `qweather-skill/` | `caoronglin/qweather-skill` | QWeather (和风天气) API skill with Python script and API reference |
| `nwafu-task-feishu/` | `caoronglin/nwafu-task-feishu` | Feishu task/schedule helper for NWAFU, MIT licensed |
| `copaw-skills/` | `caoronglin/copaw-skills` | Large CoPaw skill library (46+ skills incl. docx/pptx/xlsx/pdf, MCP connectors, channels), MIT licensed |

Each directory keeps its own `README.md`, `SKILL.md`, and license where the source had one. Refer to the per-directory README for usage.

## Layout note

No skill-level deduplication was performed. Some skills overlap across sources (for example `docx`, `pdf`, `xlsx`, `pptx`, `skill-creator`). They are kept in their original locations to avoid destructive merging; consolidate only when a deliberate mapping is decided.

## History

Built with `git subtree add --prefix=<dir> <source> HEAD`, so every source commit is reachable in this repository's history. To bring in upstream changes later:

```bash
git subtree pull --prefix=<dir> <source-remote-or-path> <branch> --squash
```

## License

Licenses are per-subdirectory. `nwafu-task-feishu/` and `copaw-skills/` ship MIT licenses in their own trees. Other sources did not include a license file; treat their terms as unspecified.
