# tableau-parser
v. 0.1.0
## About
**tableau-parser** is a tool to convert ot-tableau tableaux into HTML tables for use on the web.

This tool is being written as a part of [otbank](https://github.com/angus-lherrou/otbank).
## Recent changes

* Now supports the hand! (started to implement optional arguments in `\cand{}`)
* Outputs a whole HTML page; copy and paste the CSS and the outermost `<table>` into another html file to use the generated table elsewhere.
* Added CSS table formatting to match (roughly) ot-tableau formatting.

## To-do
* Support for nested commands
* Support for tipa maybe?
* Add class tags to everything to avoid interfering with other CSS on an arbitrary page
* Small caps constraints
* Support for bomb, shading, etc.
