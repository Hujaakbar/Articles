# SQLFluff: Reclaim your sanity and happiness

![happy man](./images/happy.jpg)
*Image by [Jake Aldridge](https://pixabay.com/users/jakealdridge-3932630/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1885144) from [Pixabay](https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1885144)*

You know oftentimes, the cause of runtime or compile errors and hours of debugging agony is all due to simply a missing semicolon. Have you ever had such experience? If you had, you are not alone. There are two ways to avoid these unfortunate situations: either become a perfect developer who never makes mistakes, or use helpful tools such as linters that can catch these errors early on.

I am nowhere near being a perfect developer who never makes a mistake. In fact, I'm probably the opposite of a perfect developer, so even if I wanted to, I wouldn’t be able to teach you how to become a perfect developer. But what I can teach you is using linters. A [Wikipedia](https://en.wikipedia.org/wiki/Lint_(software)) defines a linter as a "static code analysis tool used to flag programming errors, bugs, stylistic errors and suspicious constructs."

If you're not convinced yet on using linters, consider this scenario: in a large project with multiple members, different people tend to write code in different formats. Differing formats often make code reviews difficult and cause inconsistency in source code. It would be easier and more consistent for everyone if all team members wrote the code in the same format. A linter can help you with this issue too. Hopefully, now you see the value of using linters.

There are linters for almost every programming language. In many cases there is more than one good linters for a particular language. However, when it comes to SQL, as far as I know, there are fewer options. But it can't be a reason to feel discouraged though, [SQLFull](https://sqlfluff.com/), the most popular linter for SQL, is an excellent tool. In this article I will explain what it is and how to use it.

## SQLFLuff

SQLFluff is the most popular linter for SQL language. It touts itself as being a "SQL linter for humans". It helps not only with catching syntax errors but also *fixing* them. It supports multiple [dialects] of SQL language such as postgresql, MySQL and even **Snowflake**.
*You can find the official documentation here: [Docs][SQLFluff Docs].*

## Installation

SQLFluff can be installed as

- a [VSCode extension](https://marketplace.visualstudio.com/items?itemName=dorzey.vscode-sqlfluff)
- pre-commit hook
- command line tool
- CI/CD pipeline tool

Easier and less error-prone way of running SQLFluff is as a command line tool.
We will also discuss using it as a pre-commit hook at a later section.

### Installing SQLFluff as a command line tool

**Note:** to install SQLFluff, you need Python and pip (or any other package manager such as poetry, pipenv). This example uses pip

Install SQLFluff by running the following command on the terminal:

```shell
pip install sqlfluff
```

Check the installation by running:
(expected output is something like this: 3.2.4)

```shell
sqlfluff version
# 3.2.4
```

## Usage

SQLFluff has 3 main commands:
`lint` : this command shows the syntax errors
`format` : formats the code (mainly it fixes new line, indentation and white spaces)
`fix`: fixes the syntax errors such as missing comma, semicolon, new line etc.

To lint a file named test.sql, run:

```shell
sqlfluff lint test.sql --dialect snowflake
```

The results looks like below:

```shell
== [test.sql] FAIL
L:   1 | P:   1 | LT01 | Expected only single space before 'SELECT' keyword.
                       | Found '  '. [layout.spacing]
L:   1 | P:   1 | LT02 | First line should not be indented.
                       | [layout.indent]
L:   1 | P:   1 | LT13 | Files must not begin with newlines or whitespace.
                       | [layout.start_of_file]
L:   1 | P:  11 | LT01 | Expected only single space before binary operator '+'.
                       | Found '  '. [layout.spacing]
L:   1 | P:  14 | LT01 | Expected only single space before naked identifier.
                       | Found '  '. [layout.spacing]
L:   1 | P:  27 | LT01 | Unnecessary trailing whitespace at end of file.
                       | [layout.spacing]
L:   1 | P:  27 | LT12 | Files must end with a single trailing newline.
                       | [layout.end_of_file]
All Finished 📜 🎉!
```

Output shows test.sql file has only formatting error.

**Understanding the linting output:**

Linting output shows the `L` (line number) and `P` (position) that caused the error, and the rule index that threw the error, in this case `LT01`. After the rule index there is a short explanation as for what is the problem.
This [LT01](https://docs.sqlfluff.com/en/stable/reference/rules.html#layout-bundle) rule concerns with layout spacing and checks for inappropriate spacing such as excessive whitespace, trailing whitespace at the end of a line and also the wrong spacing between elements on the line.
*You can find all the rules and their definitions here: [Rule Index].*

SQLFluff comes with default rules. You can quickly check those rules in command line by running:

```shell
sqlfluff rules
```

It is possible to specify the rules we want to check against or exclude certain rules.

Specifying the rules:

```shell
 sqlfluff lint test.sql --rules LT02,LT12,CP01,ST06,LT09,LT01
```

Excluding rules:

```shell
sqlfluff fix test.sql --exclude-rules LT01
```

SQLFluff may not recognize some keywords certain SQl dialects uses. When it happens it throws `parsing error`. Workaround of this problem is to tell SQLFluff to ignore parsing errors.

```shell
sqlfluff fix test.sql --ignore parsing
```

*Other command line configurations can be find here: [CLI Config].*

## Config File

Configuring SQLFluff using cli may be little tedious, instead we can use config files. SQLFluff comes with [default configurations][Config File]. However, based on your preference, you can overwrite default configurations.

SQLFluff supports following config file types:

- setup.cfg
- tox.ini
- pep8.ini
- .sqlfluff
- pyproject.toml

In below example we change 7 configuration rules.
**Note:** The rest of the rules stay the same as default.

`.sqlfluff` file

```shell
[sqlfluff]

dialect = snowflake

exclude_rules = ST06

# Number of passes to run before admitting defeat
runaway_limit = 2

large_file_skip_byte_limit = 2000000

[sqlfluff:layout:type:comma]
line_position = leading
```

The same configuration in TOML file format:

```TOML
[tool.sqlfluff]

dialect = snowflake

exclude_rules = ST06

runaway_limit = 2

large_file_skip_byte_limit = 2000000

[tool.sqlfluff.layout.type.comma]
line_position = leading
```

**Explanation of the above configuration:**

`dialect = snowflake` sets the dialect of the SQLFluff to Snowflake syntax.
`exclude_rules = ST06` excludes the rule `ST06`. Rule `ST06` orders select targets in ascending complexity. For instance, it puts `*` above other select targets like below:

```SQL
select
    *,
    a,
    b,
    row_number() over (partition by id order by date) as y
from my_table;
```

However, I don't want to change the order of the columns, so I'm disabling the `ST06` rule.

`runaway_limit = 2` specifies the number of times the SQLFluff tries to find errors/improvements in a given block of code before moving on. `large_file_skip_byte_limit = 2000000` instructs SQLFluff to ignore the file if the sql file size is larger than 2000000 bytes (2MB). `line_position = leading` it puts the commas at the beginning of each line. Note, very large files can make the SQLFluff parser effectively hang.

Result of `line_position = leading` rule:

```SQL
select
    a
    ,b
    ,c
from my_table;
```

## Pre-Commit

Git is an indispensable tool for every developer. It helps with version control and collaboration. Git can also call some functions while carrying out its usual job. For example, before committing changes to a repository, git can call certain functions, these functions are called pre-commit hooks. A tool called [pre-commit] can help with setting up and configuring these functions (pre-commit hooks). We can set-up pre-commit hooks to run SQLFluff automatically whenever we try to commit our changes. If SQLFluff finds error in our sql files, it throws error and Git prevents the changes from being committed to the repository.

### Setting up pre-commit

```shell
pip install pre-commit

# check installation
pre-commit --version
# pre-commit v4.0.1
```

create a file named `.pre-commit-config.yaml`. in your repository's root directory.
Inside the file write below:

```yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: stable_version
    hooks:
      - id: sqlfluff-lint
      - id: sqlfluff-fix
```

pre-commit uses SQLFluff configurations specified in `.sqlfluff` file. But If you don't want to use `.sqlfluff` file for whatever reason, you can also write the configurations directly on `.pre-commit-config.yaml` file as below.

```yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: stable_version
    hooks:
      - id: sqlfluff-lint
        args:
            - '--dialect'
            - 'snowflake'
            - '--exclude-rules'
            - 'ST06'
            - '--runaway-limit'
            - '2'
            - '--layout-type'
            - 'comma'
            - '--line-position'
            - 'leading'

      - id: sqlfluff-fix
            args:
            - '--dialect'
            - 'snowflake'
            - '--exclude-rules'
            - 'ST06'
            - '--runaway-limit'
            - '2'
            - '--layout-type'
            - 'comma'
            - '--line-position'
            - 'leading'
```

Run `pre-commit install` to set up the git hook scripts.
Now, whenever you run `git commit`, SQLFluff linting and fixing commands will run before the commit. If SQLFluff finds no errors, commit is made, but if it finds errors commit is not made. SQlFluff outputs the errors to the terminal and fixes them as much as it can. After that you need to run `git add` and `git commit` commands once again.
*You can find more info on using SQLFluff with pre-commit here: [Pre-commit docs](https://docs.sqlfluff.com/en/latest/production/pre_commit.html).*

[SQLFluff docs]: https://docs.sqlfluff.com/en/stable/
[Rule Index]: https://docs.sqlfluff.com/en/stable/rules.html#rule-index
[Dialects]: https://docs.sqlfluff.com/en/stable/dialects.html
[CLI Config]: https://docs.sqlfluff.com/en/stable/cli.html#cliref
[Config File]: https://docs.sqlfluff.com/en/stable/configuration.html#default-configuration
[pre-commit]: https://pre-commit.com/
