# How To Use KeePassXC Cli

There are similarly named programs: KeePass, KeePassX and KeePassXC (many of which are each others' forks).

| Program   | Condition                                                                                                         |
| :-------- | :---------------------------------------------------------------------------------------------------------------- |
| KeePass   | [primarily for Windows.](https://en.wikipedia.org/wiki/KeePass)                                                   |
| KeePassX  | [no longer actively maintained.](https://www.keepassx.org/index.html%3Fp=636.html)                                |
| KeePassXC | [actively maintained and runs natively on Linux, macOS and Windows](https://github.com/keepassxreboot/keepassxc). |

Note: GUI version of the KeePassXC has more features than cli version. GUI version has variety of [shortcuts](https://keepassxc.org/docs/KeePassXC_GettingStarted#_keyboard_shortcuts) as well. Regarding how to use GUI version of the KeePassXC, visit [Getting Started Guide](https://keepassxc.org/docs/KeePassXC_GettingStarted).

Below features are available only in GUI version.

-   Setting "Name" and "Description" fields of passwords database.
-   Nesting Groups.
-   Creating entry attributes ([open issue](https://github.com/keepassxreboot/keepassxc/issues/9212)).
-   Adding Timed One-Time Passwords (TOTP).
-   Adding entry with the same title as existing entry.

KeePassXC stores all the passwords in passwords database. A passwords database (hereafter referred to as database) is an (encrypted) binary file. It can have any or no extension, but the `.kdbx` extension is commonly used. The database is encrypted with the AES encryption algorithm using a 256 bit key.
_I recommend storing KeePassXC database both in Git repository and in cloud storages such as Google Drive._

Note: Although there is no official mobile app, [KeePassDX](https://play.google.com/store/apps/details?id=com.kunzisoft.keepass.free) is a third party android app, [recommended by KeePassXC](https://keepassxc.org/docs/#faq-platform-mobile).

Table of contents:

-   [Interactive Mode vs Standalone Mode](#interactive-mode-vs-standalone-mode)
-   [Passwords Database](#passwords-database)
    -   [Create Database](#create-database)
    -   [View Database Information](#view-database-information)
    -   [Edit Database](#edit-database)
-   [Generate a random password and passphrase](#generate-a-random-password-and-passphrase)
-   [Entries](#entries)
    -   [Create and Remove Groups](#create-and-remove-groups)
    -   [Add Entry](#add-entry)
    -   [Move Entry](#move-entry)
    -   [List Entries](#list-entries)
    -   [Remove Entry](#remove-entry)
    -   [Attachments](#attachments)
    -   [Show Entry details](#show-entry-details)
    -   [Copy attribute/password to clipboard](#copy-attributepassword-to-clipboard)
    -   [Edit Entry](#edit-entry)
    -   [Search Entries](#search-entries)
-   [Other utilities](#other-utilities)
    -   [Estimate password strength](#estimate-password-strength)
-   [References](#references)

## Interactive Mode vs Standalone Mode

KeePassXC-cli has standalone and interactive modes.

Standalone mode
: In standalone mode you need to specify database path for every action. You also need to provide database password or keyfile for every single action.

Standalone mode example:

```bash
$ keepassxc-cli db-info database_file.kdbx
Enter password to unlock database_file.kdbx:
# ... info

$ keepassxc-cli some_other_action database_file.kdbx
Enter password to unlock database_file.kdbx:
# ... info
```

Interactive mode
: In interactive mode, you provide database password or keyfile only once while opening the database. Afterwards, you can perform multiple actions without providing password.

Open database in interactive mode:

```bash
$ keepassxc-cli open database_file.kdbx

Enter password to unlock database_file.kdbx:
database_file.kdbx> db-info
# ... info
database_file.kdbx> some_other_action
```

You can close open database using `close` command and open another database using `open` command within interactive mode.

You can exit from the interactive mode using `exit` and `quit` commands.

Note:

-   In interactive mode certain options such as `-h` does not work.
-   If the database is open both in interactive mode and GUI, sometimes changes may not merge properly. In such cases interactive mode throws error:
    `Unable to save database to file: Database file has unmerged changes`.

## Passwords Database

### Create Database

```bash
keepassxc-cli db-create [options] <database_path>
```

| Options                 | Description                                                                |
| :---------------------- | :------------------------------------------------------------------------- |
| -p                      | Set a password for the database.                                           |
| -t                      | Target decryption time in MS for the database. (Default 1000ms or 1second) |
| --set-key-file \<path\> | Set the key file for the database.                                         |

To create database, at least one of the `-p` or `--set-key-file` options should be used, otherwise database cannot be created.

`-p` option:

```txt
$ keepassxc-cli db-create -p path/to/database_file.kdbx

Enter password to encrypt database (optional):
Repeat password:
Successfully created new database.
```

`--set-key-file` option:

Any file can be used as a key file. It is important that key file contents must not be changed.

KeePassXC generates a key file if you specify a path to non-existent file.

```txt
$ keepassxc-cli db-create ./my_database.kdbx --set-key-file ./pass/to/my_key_file

Successfully created new database.
```

Above command creates a binary `my_key_file` file in the specified path.

Contents of the `my_key_file`

```txt
@n�瞯�+�*ӹ�&�t��1jn���n������k���
��2�����m
hig�k̇����v�of���\�FA�6!-������[����˸�3{�
��
��U���{U��s�`�V�D���� .
```

Note: You can set up both password and key file.

### View Database Information

```bash
db-info [options]
```

| Options                 | Description                                                                     |
| :---------------------- | :------------------------------------------------------------------------------ |
| -k, --key-file \<path\> | Key file of the database.                                                       |
| --no-password           | Do not prompt for password (when only key-file is used to encrypt the database) |

**NOTE:** Even if you set up only key file and no password, KeePassXC prompts you to enter a password while operating on database. If it receives no password, it throws an error. To avoid it, use `--no-password` option.

Without `--no-password` option:

```txt
$ keepassxc-cli db-info database_file.kdbx -k ./path/to/key_file
Enter password to unlock database.kdbx:
Error while reading the database: Invalid credentials were provided, please try again.
If this reoccurs, then your database file may be corrupt. (HMAC mismatch)
```

With `--no-password` option:

```txt
$ keepassxc-cli db-info database_file.kdbx -k ./path/to/key_file --no-password

# ...info
```

<details>

<summary>Interactive mode</summary>

```txt
$ keepassxc-cli open database_file.kdbx

Enter password to unlock database_file.kdbx:
database_file.kdbx> db-info
UUID: {f04605a4-6899-4219-9f10-a7d3bc7c3d25}
Name:
Description:
Cipher: AES 256-bit
KDF: AES (1000000 rounds)
Recycle bin is enabled.
Location: database_file.kdbx
Database created: 4/6/2025 12:52 AM
Last saved: 4/6/2025 10:51 AM
Unsaved changes: no
Number of groups: 1
Number of entries: 2
Number of expired entries: 0
Unique passwords: 1
Non-unique passwords: 0
Maximum password reuse: 1
Number of short passwords: 0
Number of weak passwords: 1
Entries excluded from reports: 0
Average password length: 8 characters
database_file.kdbx>
```

</details>

<details>

<summary>Standalone mode</summary>

```bash
keepassxc-cli db-info [options] <database_path>
```

```txt
$ keepassxc-cli db-info database_file.kdbx

Enter password to unlock database_file.kdbx:

UUID: {f04605a4-6899-4219-9f10-a7d3bc7c3d25}
Name:
Description:
Cipher: AES 256-bit
KDF: AES (1000000 rounds)
Recycle bin is enabled.
Location: database_file.kdbx
Database created: 4/6/2025 12:52 AM
Last saved: 4/6/2025 10:51 AM
Unsaved changes: no
Number of groups: 1
Number of entries: 2
Number of expired entries: 0
Unique passwords: 1
Non-unique passwords: 0
Maximum password reuse: 1
Number of short passwords: 0
Number of weak passwords: 1
Entries excluded from reports: 0
Average password length: 8 characters
```

</details>

If you noticed, name and description fields are empty. That's because they can be set only in GUI version and we created our database using cli.

### Edit Database

```txt
# interactive mode
db-edit [options]

# standalone mode
$ keepassxc-cli db-edit [options] <database_path>
```

| Options                 | Description                          |
| :---------------------- | :----------------------------------- |
| --set-key-file \<path\> | Set the key file for the database.   |
| --unset-key-file        | Unset the key file for the database. |
| -p, --set-password      | Set a password for the database.     |
| --unset-password        | Unset the password for the database. |
| --no-password           | Do not prompt for database password. |

To change the password, `-p` or `--set-password` options can be used.

```bash
keepassxc-cli db-edit database_file.kdbx -p

Enter password to unlock  database_file.kdbx:
Enter password to encrypt database (optional):
Repeat password:
Successfully edited the database.
```

To remove the password, use `--unset-password` option.

Note: If database does has key file set up, you cannot remove the password. Database must have at least password or key file set up at all times.

So, before removing password, set up key file.

Standalone mode:

```bash
$ keepassxc-cli db-edit database_file.kdbx --unset-password

Enter password to unlock database_file.kdbx:
Cannot remove all the keys from a database.
Could not change the database key.
```

Interactive mode:

```bash
database.kdbx> db-edit --unset-password
Cannot remove all the keys from a database.
Could not change the database key.
database.kdbx>
```

Remove key file:

```txt
 database_file.kdbx> db-edit --unset-key-file
Successfully edited the database.
 database_file.kdbx>
```

Similar to password, you cannot remove key file if database does not have password set up.

## Generate a random password and passphrase

Without opening database it is possible to generate passwords and passphrases.

### Generate a new random password

```txt
$ keepassxc-cli generate

dhUnLqWPu4EUAn2ieu35S7Ruof5NN4xT
```

| options               | Description                                  | Default status |
| :-------------------- | :------------------------------------------- | :------------- |
| -L, --length <length> | Length of the generated password             | 32 characters  |
| -l, --lower           | lowercase characters                         | enabled        |
| -U, --upper           | uppercase characters                         | enabled        |
| -n, --numeric         | numbers                                      | enabled        |
| -s, --special         | special characters                           | disabled       |
| -e, --extended        | extended ASCII                               | disabled       |
| -x, --exclude <chars> | Exclude character set                        | disabled       |
| --exclude-similar     | Exclude similar looking characters           | disabled       |
| --every-group         | Include characters from every selected group | disabled       |
| -c, --custom <chars>  | Use custom character set                     | disabled       |

By default generated password contains 32 characters consisted of numbers and upper and lowercase letters.

**Note:** When above options are used, they are not appended to default options. For example using `-s` option doesn't not make it `-L32 -lUns`, instead it becomes `-L32 -s`.

Special character only password:

```txt
$ keepassxc-cli generate -L 25 -s
:}*?.:''~?<!-#&,(-%^&;(>=
```

Lowercase character only password:

```bash
$ keepassxc-cli generate -l
aitnxfrgqmnektaiifxkeeqpyrsiuftt
```

Extended ASCII character only password:

```txt
$ keepassxc-cli generate -e
Ç¬¯¤¿Éú«¥þÇ¬ä¥õòõ½ä®ÖîÃ¡ðÄâ½ÑÖ®ì
```

`--every-group` option seems to have no effect

```txt
$ keepassxc-cli generate --every-group
HAesp2cKtAvyEuOXlU63hxIy16nbsigO

$ keepassxc-cli generate -n --every-group
48265619111096272946632565481695

$ keepassxc-cli generate -s --every-group
&:_:|"+$$#~\+|."{:,@"+%/@_#,)}?_
```

To generate a password that contains upper and lowercase alphanumeric characters and special characters, use below options:

```txt
$ keepassxc-cli generate -lUns
P?M~gbU'E7eXKP-Vv[[RUg7,e:Dv:uXi
```

### Generate a random passphrase

```txt
$ keepassxc-cli diceware
krypton flashily groggy wobble undertake napkin woven
```

| Options                  | Description                             |
| :----------------------- | :-------------------------------------- |
| -W, --words \<count\>    | Word count for the diceware passphrase. |
| -w, --word-list \<path\> | Wordlist for the diceware generator.    |

By default it generates 7 word passphrase. You can specify word count using `-W` or `--words` options.

```txt
$ keepassxc-cli diceware -W 3
imposing chance resubmit
```

## Entries

KeePassXC refers to passwords as entries.

Before discussing how to create entries and more, let's review a few concepts, namely entries, attributes, groups, notes and attachments.

Entry
: Entry is a record. Each entry can contain various fields such as usernames, passwords, URLs, attachments, attributes, and notes.

Groups
: Entries can be organized into groups. Groups can be nested. The default (root) group is `Passwords`. There is also group called `Recycle Bin`, where deleted groups and entries are stored.
: Note: Groups can be nested only in GUI version.
: Format: group_name/entry_name.

Notes
: Notes are additional information. Store less sensitive data in notes.

Attributes
: Attributes are additional information in key-value format. By default attribute values are hidden just like passwords. Unlike notes, you can store sensitive data in attributes.
: Note: attributes can be created only in GUI version.

Attachments
: Entries can include attachments. Attachments are added to the database and stored as encrypted binaries.

### Create and Remove Groups

Groups are like folders. They store entries.

```txt
# create group
mkdir [options] <database> <group>

# remove group
rmdir [options] <database> <group>
```

| Options                 | Description                          |
| :---------------------- | :----------------------------------- |
| --no-password           | Do not prompt for database password. |
| -k, --key-file \<path\> | Key file of the database.            |

Note: When a group is removed, it will be moved to recycle bin. If the group is already in recycle bin, then it will be permanently deleted.

Create group:

```bash
database.kdbx> mkdir social_media
Successfully added group social_media.
database.kdbx> mkdir temp
Successfully added group temp.
database.kdbx>
```

Remove group:

```bash
database.kdbx> rmdir temp
Successfully recycled group temp.
database.kdbx>
```

Remove the group from recycle bin:

```txt
$ keepassxc-cli rmdir database.kdbx "Recycle Bin/temp"
Enter password to unlock database.kdbx:
Successfully deleted group Recycle Bin/temp.
```

### Add Entry

You can add new entry using `add` command

| Options                     | Description                        |
| :-------------------------- | :--------------------------------- |
| -u, --username \<username\> | Username for the entry.            |
| --url \<URL\>               | URL for the entry.                 |
| --notes \<Notes\>           | Notes for the entry.               |
| -p, --password-prompt       | Prompt for the entry's password.   |
| -g, --generate              | Generate a password for the entry. |

If you don't provide `-p` option, entry will be created without password.

You can provide `-g` option to generate password. While generating password, you can use above-discussed options to specify character lengths, types of characters used etc.

Note: There is no option to provide randomly generated passphrase.

<details>

  <summary>Standalone mode</summary>

```txt
keepassxc-cli add <database> <entry name> [options]
```

Example :

```bash
$ keepassxc-cli add database.kdbx first_entry -u username@gmail.com --url google.com --notes "Some notes" -p

Enter password to unlock database.kdbx:
Enter password for new entry:
Successfully added entry first_entry.
```

Generate random password while adding entry:

```txt
$ keepassxc-cli add database.kdbx entry_with_random_password  -u username:hotmail.com -g -L20
Enter password to unlock database.kdbx:
Successfully added entry entry_with_random_password.
```

</details>

<details>

  <summary>Interactive mode</summary>

```txt
add <entry name> [options]
```

```sh
keepassxc-cli open database.kdbx
Enter password to unlock database.kdbx:
database.kdbx> add second_entry -u username@gmail.com  --url google.com --notes "Some notes providing extra info" -p
Enter password for new entry:
Successfully added entry second_entry.
database.kdbx>
```

</details>

Note: Adding entry with the same title as existing entry is supported only in GUI version.

Adding randomly generated password while adding new entry:

```txt
database.kdbx> add entry_with_random_pswrd -u username@mail.com -g -L10 -lUns
Successfully added entry entry_with_random_pswrd.
database.kdbx>
```

Creating new entry within a group:

```bash
database.kdbx> add social_media/my_entry -u example@hotmail.com
Successfully added entry my_entry.
database.kdbx>
```

Note:

1. Group must exist.
1. Timed One-Time Passwords (TOTP) can be added only in GUI version.
1. Although KeePassXC supports TOTP, storing TOTP codes in the same database as the password will eliminate the advantages of two-factor authentication. If KeePassXC database is compromised in some way, adversary can get the hold of both the primary password and TOTP. For this reason either use a separate application for TOTP such as Google Authenticator or store TOTP codes in a separate database that you only unlock when needed.

### Move Entry

```txt
mv [options] <database> <entry> <group>
```

| Options                 | Description                          |
| :---------------------- | :----------------------------------- |
| --no-password           | Do not prompt for database password. |
| -k, --key-file \<path\> | Key file of the database.            |

Example:

```txt
database.kdbx> mv entry_with_random_pswrd social_media
Successfully moved entry entry_with_random_pswrd to group social_media.
database.kdbx>
```

Move entry from one group to another

```txt
database.kdbx> mv social_media/my_entry financial
Successfully moved entry my_entry to group financial.
database.kdbx>
```

Note: Groups can be moved (nested) only in GUI version.

### List Entries

```txt
ls [options] <database> [group_name]
```

Lists the contents of a group in a database. If group name is not specified, it will default to the root (Passwords) group.

| Options                 | Description                                 |
| :---------------------- | :------------------------------------------ |
| -R, --recursive         | Recursively list the elements of the group. |
| -f, --flatten           | Flattens the output to single lines.        |
| --no-password           | Do not prompt for database password.        |
| -k, --key-file \<path\> | Key file of the database.                   |

<details>

  <summary>Standalone mode</summary>

```txt
keepassxc-cli ls database.kdbx
Enter password to unlock database.kdbx:
first_entry
second_entry
entry_with_random_password
Recycle Bin/
social_media/
financial/
```

</details>

<details>

  <summary>Interactive mode</summary>

```txt
database.kdbx> ls
first_entry
second_entry
entry_with_random_password
Recycle Bin/
social_media/
financial/
database.kdbx>
```

</details>

List entries of certain group

```txt
database.kdbx> ls social_media
entry_with_random_pswrd
database.kdbx>
```

Show entries recursively

```txt
database.kdbx> ls -R
first_entry
second_entry
entry_with_random_password
Recycle Bin/
  password1
  okay
social_media/
  entry_with_random_pswrd
financial/
  my_entry
  bank1
database.kdbx>
```

Show entries recursively in an single line (without nested tree structure):

```txt
database.kdbx> ls -Rf
first_entry
second_entry
entry_with_random_password
Recycle Bin/
Recycle Bin/password1
Recycle Bin/okay
social_media/
social_media/entry_with_random_pswrd
financial/
financial/my_entry
financial/bank1
database.kdbx>
```

### Remove Entry

command: `rm`

| Options                 | Description                          |
| :---------------------- | :----------------------------------- |
| --no-password           | Do not prompt for database password. |
| -k, --key-file \<path\> | Key file of the database.            |

Example:

```txt
database.kdbx> rm financial/my_entry
Successfully recycled entry my_entry.
database.kdbx>
```

### Attachments

#### Add attachment to an entry

Syntax:

```bash
attachment-export [options] <database> <entry> <attachment_name> <export_file>
```

Standalone mode:

```sh
keepassxc-cli attachment-import <database> <entry> <attachment-name> <attachment path>
```

Interactive mode

```bash
database.kdbx> attachment-import <entry> <attachment-name> <attachment path>
```

| Options     | Description                     |
| :---------- | :------------------------------ |
| -f, --force | Overwrite existing attachments. |

Example:

Let's say I want to attach a PGP key file as an attachment to the `second_entry`.

pgp_file.txt

```txt
-----BEGIN PGP PRIVATE KEY BLOCK-----
lFgEXEcE6RYJKwYBBAHaRw8BAQdArjWwk3FAqyiFbFBKT4TzXcVBqPTB3gmzlC/U
b7O1u10AAP9XBeW6lzGOLx7zHH9AsUDUTb2pggYGMzd0P3ulJ2AfvQ4RtCZBbGlj
ZSBMb3ZlbGFjZSA8YWxpY2VAb3BlbnBncC5leGFtcGxlPoiQBBMWCAA4AhsDBQsJ
CAcCBhUKCQgLAgQWAgMBAh4BAheAFiEE64W7X6M6deFelE5j8jFVDE9H444FAl2l
nzoACgkQ8jFVDE9H447pKwD6A5xwUqIDprBzrHfahrImaYEZzncqb25vkLV2arYf
a78A/R3AwtLQvjxwLDuzk4dUtUwvUYibL2sAHwj2kGaHnfICnF0EXEcE6RIKKwYB
BAGXVQEFAQEHQEL/BiGtq0k84Km1wqQw2DIikVYrQrMttN8d7BPfnr4iAwEIBwAA
/3/xFPG6U17rhTuq+07gmEvaFYKfxRB6sgAYiW6TMTpQEK6IeAQYFggAIBYhBOuF
u1+jOnXhXpROY/IxVQxPR+OOBQJcRwTpAhsMAAoJEPIxVQxPR+OOWdABAMUdSzpM
hzGs1O0RkWNQWbUzQ8nUOeD9wNbjE3zR+yfRAQDbYqvtWQKN4AQLTxVJN5X5AWyb
Pnn+We1aTBhaGa86AQ==
=n8OM
-----END PGP PRIVATE KEY BLOCK-----
```

<details>

<summary>Standalone mode</summary>

```txt
$ keepassxc-cli attachment-import database.kdbx second_entry pgp_key ./pgp_file.txt
Enter password to unlock database.kdbx:
Successfully imported attachment ./pgp_file.txt as pgp_key to entry second_entry.
```

</details>

<details>

<summary>Interactive mode</summary>

```txt
database.kdbx> attachment-import first_entry pgp_private_key ./pgp_file.txt
Successfully imported attachment ./pgp_file.txt as pgp_private_key to entry first_entry.
database.kdbx>
```

</details>

#### Export attachment

Export the content of an attachment to a specified file

```txt
attachment-export [options] <database> <entry> <attachment_name> <export_file>
```

| Options  | Description             |
| :------- | :---------------------- |
| --stdout | export to standard out. |

Export to standard out (in standalone mode):

```txt
keepassxc-cli attachment-export database.kdbx second_entry pgp_key --stdout
Enter password to unlock database.kdbx:
-----BEGIN PGP PRIVATE KEY BLOCK-----
lFgEXEcE6RYJKwYBBAHaRw8BAQdArjWwk3FAqyiFbFBKT4TzXcVBqPTB3gmzlC/U
b7O1u10AAP9XBeW6lzGOLx7zHH9AsUDUTb2pggYGMzd0P3ulJ2AfvQ4RtCZBbGlj
ZSBMb3ZlbGFjZSA8YWxpY2VAb3BlbnBncC5leGFtcGxlPoiQBBMWCAA4AhsDBQsJ
CAcCBhUKCQgLAgQWAgMBAh4BAheAFiEE64W7X6M6deFelE5j8jFVDE9H444FAl2l
nzoACgkQ8jFVDE9H447pKwD6A5xwUqIDprBzrHfahrImaYEZzncqb25vkLV2arYf
a78A/R3AwtLQvjxwLDuzk4dUtUwvUYibL2sAHwj2kGaHnfICnF0EXEcE6RIKKwYB
BAGXVQEFAQEHQEL/BiGtq0k84Km1wqQw2DIikVYrQrMttN8d7BPfnr4iAwEIBwAA
/3/xFPG6U17rhTuq+07gmEvaFYKfxRB6sgAYiW6TMTpQEK6IeAQYFggAIBYhBOuF
u1+jOnXhXpROY/IxVQxPR+OOBQJcRwTpAhsMAAoJEPIxVQxPR+OOWdABAMUdSzpM
hzGs1O0RkWNQWbUzQ8nUOeD9wNbjE3zR+yfRAQDbYqvtWQKN4AQLTxVJN5X5AWyb
Pnn+We1aTBhaGa86AQ==
=n8OM
-----END PGP PRIVATE KEY BLOCK-----

```

Export to a file (in interactive mode):

```bash
database.kdbx> attachment-export second_entry pgp_key ./temp.txt
Successfully exported attachment pgp_key of entry second_entry to ./temp.txt.
database.kdbx>
```

#### Remove attachment from an entry

```sh
# Standalone mode
keepassxc-cli attachment-rm <database> <entry> <attachment_name>

# Interactive mode
database.kdbx> attachment-rm <entry> <attachment_name>
```

Interactive mode:

```txt
database.kdbx> attachment-rm first_entry pgp_private_key
Successfully removed attachment pgp_private_key from entry first_entry.
database.kdbx>
```

### Show Entry details

`show` command.

| Options                             | Descriptions                                              |
| :---------------------------------- | :-------------------------------------------------------- |
| -t, --totp                          | Show the entry's current TOTP.                            |
| -a, --attributes \<attribute_name\> | Names of the attributes to show.                          |
| -s, --show-protected                | Show password and the protected attributes in clear text. |
| --all                               | Show all the attributes of the entry.                     |
| --show-attachments                  | Show the attachments of the entry.                        |

<details>

<summary>Standalone mode</summary>

```txt
keepassxc-cli show database.kdbx first_entry
Enter password to unlock database.kdbx:
Title: first_entry
UserName: username@gmail.com
Password: PROTECTED
URL: google.com
Notes: Some notes providing extra info
Uuid: {98606c7d-4d9d-4000-8ba6-161079a70fbb}
Tags:
```

</details>

<details>

<summary>Interactive mode</summary>

```txt
database.kdbx> show second_entry
Title: second_entry
UserName: username@gmail.com
Password: PROTECTED
URL: google.com
Notes: Some notes providing extra info
Uuid: {575833c4-cd0b-4fff-b4d0-86a2adfe7d7d}
Tags:
database.kdbx>
```

</details>

By default `show` command does not show attribute and attachments names.
To see attribute names, use `--all` option:

```txt
database.kdbx> show second_entry --all
Title: second_entry
UserName: username@gmail.com
Password: PROTECTED
URL: google.com
Notes: Some notes providing extra info
Uuid: {575833c4-cd0b-4fff-b4d0-86a2adfe7d7d}
Tags:
attribute1: PROTECTED
attribute2: PROTECTED
database.kdbx>
```

To see attachments, use `--show-attachments` option:

```txt
database.kdbx> show second_entry --show-attachments
Title: second_entry
UserName: username@gmail.com
Password: PROTECTED
URL: google.com
Notes: Some notes providing extra info
Uuid: {575833c4-cd0b-4fff-b4d0-86a2adfe7d7d}
Tags:

Attachments:
  pgp_key (763 B)
database.kdbx>
```

#### Showing password and attribute values

By default KeePassXC-cli does not show password and attribute values.

##### Show password

```txt
database.kdbx> show second_entry -s
Title: second_entry
UserName: username@gmail.com
Password: entry2
URL: google.com
Notes: Some notes providing extra info
Uuid: {575833c4-cd0b-4fff-b4d0-86a2adfe7d7d}
Tags:
database.kdbx>
```

##### Show attribute values

Remember attributes are key-value formatted data that can be attached to entries. Attributes can be added and removed only via GUI version.
This `second_entry` entry has two attributes: `attribute1` and `attribute2`.

Showing specific attribute value:

```txt
database.kdbx> show second_entry -a attribute2
xxyyzzz
database.kdbx>
```

Showing all attribute values (with password):

```txt
database.kdbx> show second_entry -s --all
Title: second_entry
UserName: username@gmail.com
Password: entry2
URL: google.com
Notes: Some notes providing extra info
Uuid: {575833c4-cd0b-4fff-b4d0-86a2adfe7d7d}
Tags:
attribute1: secret attribute value
attribute2: xxyyzzz
database.kdbx>
```

### Copy attribute/password to clipboard

| Options                    | Description                                                       |
| :------------------------- | :---------------------------------------------------------------- |
| -a, --attribute \<attr\>   | Copy the given attribute to the clipboard.                        |
| -t, --totp                 | Copy the current TOTP to the clipboard (equivalent to "-a totp"). |
| [timeout value in seconds] | Optional timeout value, default 10 seconds                        |

KeePassXC-cli automatically clears the clipboard in given timeout (default 10 second). To disable timeout, set it to 0.

Copying attribute value to clipboard:

```txt
database.kdbx> clip second_entry -a attribute2
Entry's "attribute2" attribute copied to the clipboard!
Clearing the clipboard in 4 seconds...
```

If no attribute name is provided, password is copied to clipboard.
Copying password value to clipboard:

```txt
database.kdbx> clip second_entry 90
Entry's "Password" attribute copied to the clipboard!
Clearing the clipboard in 84 seconds...
```

### Edit Entry

Syntax:

```bash
edit [options] <database> <entry>
```

| Options                    | Description                       |
| :------------------------- | :-------------------------------- |
| -u, --username \<username> | Username for the entry.           |
| --url \<URL>               | URL for the entry.                |
| --notes \<Notes>           | Notes for the entry.              |
| -p, --password-prompt      | Prompt for the entry's password.  |
| -t, --title \<title>       | Title for the entry.              |
| -g, --generate             | Generate a password for the entry |

```bash
database.kdbx> ls
first_entry
second_entry
entry_with_random_password
Recycle Bin/
social_media/
financial/
database.kdbx>
```

Changing entry name:

```bash
database.kdbx> edit entry_with_random_password -t third_entry
Successfully edited entry third_entry.
database.kdbx>
```

Result:

```bash
database.kdbx> ls
first_entry
second_entry
third_entry
Recycle Bin/
social_media/
financial/
database.kdbx>
```

### Search Entries

```bash
search <database> <term>
```

To get better results use at least two characters as a search term.

```txt
database.kdbx> search pass
/entry_with_random_password
/Recycle Bin/password1
database.kdbx>

#######

database.kdbx> search fi
/first_entry
database.kdbx>
```

## Other utilities

### Estimate password strength

Password strength can be specified by bits of entropy. Bits of entropy measure how difficult a password is to crack in a brute force attack.

Formula:

```math
Entropy = Length × log_2(Range)
```

-   **Range** is the possible range of character types in the password.
-   **Length** is password length.

| Password Type                                   | Total Character Range |
| :---------------------------------------------- | :-------------------- |
| Arabic numerals (0–9)                           | 10                    |
| Hexadecimal numerals (0–9, A–F)                 | 16                    |
| Case insensitive Latin alphabet (a–z or A–Z)    | 26                    |
| Case insensitive alphanumeric (a–z or A–Z, 0–9) | 36                    |
| Case sensitive Latin alphabet (a–z, A–Z)        | 52                    |
| Case sensitive alphanumeric (a–z, A–Z, 0–9)     | 62                    |
| All ASCII printable characters except space     | 94                    |
| All ASCII printable characters                  | 95                    |

A password with 42 bits of entropy would require $2^{42}$ (over 4 trillion) attempts to crack in a brute force attack. It might seem a lot of attempts but hundreds of billions of password guesses can be easily tried per second. For this reason, a password should have over 100 bits of entropy.

> Increasing the entropy of the password by one bit doubles the number of guesses required, making an attacker's task twice as difficult.
>
> _Source: [Wikipedia](https://en.wikipedia.org/wiki/Password_strength#Entropy_as_a_measure_of_password_strength)_

```txt
$ keepassxc-cli estimate my-strong-password
Length 18       Entropy 31.975  Log10 9.625

$ keepassxc-cli estimate eb7NyrFWtKUmU4D5auWrsUv4TTbsqAxU
Length 32       Entropy 161.669 Log10 48.667
```

**Note:** if the password contains special characters, the keepassxc-cli might get confused.

```txt
$ keepassxc-cli estimate P?M~gbU'E7eXKP-Vv[[RUg7,e:Dv:uXi
>
>
>
```

To solve above issue, enclose the password in **double** quotes:

```txt
$ keepassxc-cli estimate "P?M~gbU'E7eXKP-Vv[[RUg7,e:Dv:uXi"
Length 32       Entropy 195.086 Log10 58.727
```

**Advanced analysis:**

```txt
$ keepassxc-cli estimate -a myStrongPassword_1_ptkyzw
Length 25       Entropy 78.518  Log10 23.636
  Multi-word extra bits 8.0
  Type: Dictionary       Length 2       Entropy  3.807 (1.15)   my
  Type: Dictionary       Length 6       Entropy 10.152 (3.06)   Strong
  Type: Dictionary       Length 8       Entropy  2.000 (0.60)   Password
  Type: Bruteforce       Length 1       Entropy  6.570 (1.98)   _
  Type: Dict+Leet        Length 1       Entropy  2.000 (0.60)   1
  Type: Bruteforce       Length 7       Entropy 45.989 (13.84)  _ptkyzw
```

---

## References

You can find a full cli documentation [here](https://github.com/keepassxreboot/keepassxc/blob/latest/docs/man/keepassxc-cli.1.adoc).

Cli commands:

| Command           | Description                                                                   |
| :---------------- | :---------------------------------------------------------------------------- |
| add               | Add a new entry to a database.                                                |
| analyze           | Analyze passwords for weaknesses and problems.                                |
| attachment-export | Export an attachment of an entry.                                             |
| attachment-import | Imports an attachment to an entry.                                            |
| attachment-rm     | Remove an attachment of an entry.                                             |
| clip              | Copy an entry's attribute to the clipboard.                                   |
| close             | Close the currently opened database.                                          |
| db-create         | Create a new database.                                                        |
| db-edit           | Edit a database.                                                              |
| db-info           | Show a database's information.                                                |
| diceware          | Generate a new random diceware passphrase.                                    |
| edit              | Edit an entry.                                                                |
| estimate          | Estimate the entropy of a password.                                           |
| export            | Exports the content of a database to standard output in the specified format. |
| generate          | Generate a new random password.                                               |
| help              | Display command help.                                                         |
| import            | Import the contents of an XML database.                                       |
| ls                | List database entries.                                                        |
| merge             | Merge two databases.                                                          |
| mkdir             | Adds a new group to a database.                                               |
| mv                | Moves an entry to a new group.                                                |
| open              | Open a database.                                                              |
| rm                | Remove an entry from the database.                                            |
| rmdir             | Removes a group from a database.                                              |
| search            | Find entries quickly.                                                         |
| show              | Show an entry's information.                                                  |
