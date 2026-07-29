# Local patch: retain the first Markdown-table data row

Applied to the DataCharts GitHub release tag `1.0.3` (`75d454b131f83abb220bc848b5ca85908d5dc996`).

The upstream table parser finds the header before starting its row counter. Its first data row is consequently counter value `3`, but the original condition only accepted rows greater than `3`. The local build changes that condition to `currentRow > 2` in `helpers/parser.ts`.

This Vault's installed `main.js` was rebuilt from that tag after the source changes. Its SHA-256 is `92e307ab1d7eacb162521d23595ad687883bc8d68f72169f4fcf693e13b67e0c`; the unmodified release asset SHA-256 was `831864e7d4ef8fb60a42a4ec4e3733c9eb136511037fa279ae711368ec334963`.

The local build also standardizes chart typography: titles use the Obsidian interface font at 16px, axis titles use 12px, and tick labels use 11px. Vault-level defaults set a 360px canvas with 16px padding, 14px corner radius, and 16px vertical margin. Individual chart blocks must still supply their own title, axis labels, and units.

## Upgrade rule

Do not overwrite `main.js` with an upstream update without first checking whether this off-by-one condition has been fixed upstream. If it has not, reapply this patch to the new release source and rebuild.
