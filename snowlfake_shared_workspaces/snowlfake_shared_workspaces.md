# Snowflake New Editor (Private and Shared Workspaces)

Snowflake introduced a new file editor called workspaces.
It makes the file organization easier via folders. Since it also includes the Database explorer and Query history panes, it also makes the database object exploration and query inspection easier.

There are two types of workspaces: (private) workspaces and shared workspaces.

## (Private) Workspaces

1. Private to a workspace owner (only owner can see and access the workspace files).
2. Workspaces are stored in an automatically created, user-specific database. This database stores the private workspaces only, nothing else.
3. It is possible to create all types of files (sql files, python files, javascript, shell files etc.)
4. It is possible to create folders, and nest folders. Drag and dropping files is possible.
5. AI Copilot is enabled.
6. It is possible to use version control (git, github) to manage version history.

Soon workspaces will be a default editor in Snowflake.

## Shared Workspaces

The same as private workspace, but has two differences:

1. Shared workspaces can be created on regular databases that store other objects too such as tables.
The creator of the workspace can choose the database and schema to create the workspace on.
2. Multiple users can access the shared workspace. Access is managed by Roles.
If one user modifies a shared workspace file, other users can see it.
Users can bring files to shared workspace from their private workspaces.

### Usage

Shared workspace editor does not support real time multi-user editing.
When one user starts to edit the file, the user gets the copy of that file as a draft. The changes will be visible only to that user.  Only after the user publishes the changed file, the changes will be visible to other users too.

Changes such uploading, renaming, and deleting files and/or folders do not require publishing.

Before publishing a file, it is possible to compare the draft against the latest published version of the file using `Show differences` feature.

Shared workspaces store all the version history. It is possible to see older versions of the files and revert a file to previous versions.

Basically The shared workspaces workflow is very similar to git workflow:

- user has to publish (similar to git push) their changes to make their changes visible to other team members.
- while user A is editing a file, if user B modified the same file and pushed the modified file, conflicts may arise when user A tries to publish his/her changes.
- workspace contains the version history and allows restoring older versions

### Permissions and Access Control

Shared workspaces use role based access control.

To create a shared workspace a role should have either of the below permissions:

- `USAGE on the database and schema` and `CREATE WORKSPACE on the schema`
- `OWNERSHIP` of the target schema

#### Granting & Revoking access to shared workspace

It is possible to grant and revoke access to workspaces using both GUI and sql command.

Graphical user interface:

Using `Configure workspace` setting, you can add and remove roles, effecting granting and revoking access to shared workspace to those roles.

Using sql command:

```sql
GRANT WRITE ON WORKSPACE <workspace_name> TO ROLE <role_name>;

REVOKE WRITE ON WORKSPACE <workspace_name> FROM ROLE <role_name>;
```

In addition to `WRITE` privilege, a role also needs the `USAGE` privilege on the database where the shared workspace is located.
