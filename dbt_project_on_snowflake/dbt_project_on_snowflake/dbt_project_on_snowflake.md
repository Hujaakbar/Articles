# dbt Projects on Snowflake

Now, it is possible to store dbt projects in Snowflake. In this blogpost, we will explore this new feature.

A dbt project is a set of related files that contains `dbt_project.yml`, `profiles.yml` and asset files like models.
Snowflake allows storing dbt project as a schema object. The files that belong to one dbt project is grouped together and treated as one unit (schema level object). This feature is called "[dbt Projects on Snowflake](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake)".

## How to Create dbt projects on Snowflake

### Step 1: Upload Source Files

The dbt project source files can be in any one of the following locations:

- An internal named stage
- A Git repository stage
- An existing dbt project object
- A workspace for dbt on Snowflake

#### Extra information regarding some of the above locations

A Git repository stage:
 Snowflake supports cloning remote Git repositories. The Git repository clone in Snowflake acts as a local Git repository with a full clone of the remote repository, including branches, tags, and commits. One benefit of having Git repository clone in Snowflake is you can easily import repository files into Snowflake functions and stored procedures. See more details on [this Snowflake page](https://docs.snowflake.com/en/developer-guide/git/git-overview).

A workspace on Snowflake:
 There are two types of private workspaces on Snowflake: local and remote Git repository-integrated.

- In local workspace, all the files are local to Snowflake. Files are stored only in Snowflake.
- In remote Git repository integrated workspace, workspace essentially becomes an editor with a clone of remote repository. Files are stored both in remote Git repository and Snowflake. (The difference between Git integrated workspace and Git repository stage is that former has editor.) Git integrated workspace has UI comments that enable git functionality like fetching, pushing etc.

#### Connecting to Remote Git Repositories

To connect to Remote Git Repositories below Snowflake objects/settings are necessary:

- An API integration
- If a repository is private, a secret
- A network rule
- An external access integration that references the network rule

### Step 2: Deploy (Create) dbt Project

After *copying* the source files to Snowflake, they can be deployed as a dbt project in a schema. Here the word "deploying" means storing/saving the source files in Snowflake schema as a single unit. It does not mean running the dbt project.

Example deployment of dbt project when the source files are in Snowflake Workspaces.

Note: Snowflake workspaces have UI components that allow deployment.

```sql
CREATE DBT PROJECT some_db.xyz_schema.my_dbt_project
  FROM 'snow://workspace/user$.public."My DBT Project"/versions/live/'
```

Each time a dbt project is deployed, Snowflake creates a version specification starting at Version$1. Each time dbt project is altered, version is updated by one.

## Executing/Running dbt Project

Once dbt Project is deployed/saved in schema, it can be executed. It is possible to execute using sql statements.

 ```sql
EXECUTE DBT PROJECT my_database.my_schema.my_dbt_project args='run --target prod';
```

It is also possible to wrap above command with Snowflake Procedures and Tasks. Tasks can be scheduled to create CI/CD pipeline.

## No-Auto Updates

When you edit source code either on the workspaces or git repository, the changes are not reflected on the dbt Project. Remember dbt Project is a copy of the source files attached to specific schema. To make your changes apply to the dbt project, you must deploy it again (which create a new version of the dbt project).

## Pros and Cons of dbt Project on Snowflake

It is difficult to find clear benefit of dbt Project on Snowflake. Only one potential benefit might exist:

Security: **keeping the dbt project source code within snowflake where actual data is stored can be argued to be more secure.** In this case, source files should be edited in a local workspaces. If collaboration is needed, shared workspaces should be used.

  However, Git hosting services like GitHub, AWS Code Commit and others provide equally high security for storing the source code. Then the argument might switch to "managing two platforms instead of one introduces more friction and potential risk due to user/configuration error". In reality, however, most companies already use multiple platforms in their tech stack. Besides using Snowflake local workspaces also means not being able to use editor extensions or command line tools like sqlfluff.

While **scheduling and combining the dbt project execution with other actions on Snowflake using tasks** might be considered an advantage, but it is not necessarily unique. Most Git hosting platforms have CI/CD features that support scheduled execution. So, this cannot be counted as a clear advantage. As for the combining the execution of the other actions such as stored procedures with dbt project execution, it can also be achieved using dbt `on-run-start` and `on-run-end` hooks.
Besides, in dbt project on Snowflake, (does not matter whether using local workspaces, Git integrated workspaces or Git repository stage), when a source files are altered, dbt Project needs to be (re)deployed. It is a friction.

## Conclusion

In rare cases, having a requirement of keeping the source code where the data resides, it might be clear or only option. Other than that, dbt Project on Snowflake does not provide clear advantage over existing solutions.
