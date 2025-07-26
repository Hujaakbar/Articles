# Version Control Systems (Part I): Local Version Control Systems

When you hear "version control" or "version control systems", you might immediately think of git. You may be already using Git and GitHub since they are now de facto industry standards. But do you know other version control systems exists too, how about the history of version control systems?

Alternatively, you may have almost no idea what version control is. You might have come across words like Version Control, Source Control, Git, GitHub, SVN, and all the other terms. You might have wondered what they all meant.

Throughout this multi-part post you will learn what version control is, version control systems, popular platforms built on the top of the version control systems and much more.

Then, let's get started!

In part one of this multi-part version control series post, we will learn below concepts:

**Table of contents:**

- [What is Version Control](#what-is-version-control)
- [Version Control Systems](#version-control-systems)
- [Local Version Control Systems](#local-version-control-systems-lvcs)

## What is Version control

Version Control (also known as Revision Control/Source Control) is a practice of managing different versions of digital files in an organized and efficient manner.

*You can think of version control as **"Efficient management of archives"**.*

With version control, you can easily switch back and forth between different versions. In version controlled environment, if you've made a mistake and want to revert back to the state/version of your files let's say two weeks ago, you can do so easily.

Note: In software development, the term "Version control" is used interchangeably with other terms such as "Source code control", and "Source code management".

Now we know what version control means, it is time to learn about version control systems.

## Version control Systems

A version control system is a software that implements version control concept i.e efficient management of archives.
Every version control system has to have two core functionalities:

1. viewing old versions
1. reverting a file to its previous version.

Applications like Microsoft Word, web applications like Notion, and platforms like Snowflake etc. have builtin and automatically managed version control systems. What it means is that you do not have to instruct these applications to save a specific version of your files (as archive). These applications automatically take snapshots of your files and save them as versions.

However, not every application includes automatic version controlling. Besides, in software development we want to be in control of how, when and which files are saved in the version control. So, we will learn this *manual* version of version control systems.

All version control systems (software) save the changes specific to a particular version  with most or all of the following metadata:

- version id
- who made the changes
- what changes were made
- the timestamp that the version is being saved at
- and more.

Note: It should be emphasized that we as a user instruct the version control system to save the changes (i.e. current version of the files). After that, a version control system saves the current version of the files along with the metadata.

## Types of Version Control Systems

There are three types of version control systems:

- Local version control systems (LVCS)
- Centralized version control systems (CVCS)
- Distributed version control systems (DVCS)

Before continuing the discussion of version control systems further, let's learn some essential terminologies.

> Note: There are many version control systems, and each of them has its own interpretation of below terminologies. To make this post practical, I will use explanation geared towards most commonly used version control system, git. (Nuances will be explained later.)

**Change:**
: A modification to a file/files.

**Initialize:**
: To create a new, empty repository.

**Repository:**
: Version control systems store all the data and metadata of the files in a folder referred to as "repository". A folder is considered a repository if a version control system has been initialized to track changes in that folder.
: In simple words, a **repository** is a folder that

: - stores a set of *ordinary* files
: - stores version-control-system-created files that contain the metadata and history of changes made to those *ordinary* files.

**Working copy:**
: The working copy is *unsaved* state of the repository. You should distinguish between saving the file by an operating system and saving the **state/version** of the the file by version control systems. Your operating system stores/saves only the final version of your files.  On the other hand, version control system (VSC) stores multiple versions of the same files.
: For example, suppose in our repository there is a file, `main.py` with 10 lines of a code, and currently it is on its 2nd version. We added 100 lines of code to this file, but, we haven't saved it as a 3rd version of the file yet. This is called a **working copy** of the file.
In other words, working copy of a repository contains changes that version control system hasn't saved yet.
: As the name implies, it is a working/unfinished version of the file. We are not ready yet to save/archive the this working copy of the file as a new version.

**to Commit (verb):**
: Version control system (VCS) automatically tracks files by watching for changes between current state of our repository and
its last saved version. If some files in the reposity are modified, version control system notices it, but it does not save
these changes automatically. Rather we as a user should instruct the VCS to save these changes as a new version (of the files).
This action of instructing VCS to store the changes is called **committing**.
The collection of these changes specific to a version is called a commit (noun).
: VCS also creates a metadata containing the timestamp that commit was made, and who made it and some other info.

**a Commit (noun):**
: The collection of changes specific to a version is called a **commit**.  A commit contains metadata that usually consists of commit id, the author information who made the commit, and a commit message that describes the change.

**Commit message:**
: A short message, written by the commit author, that describes the commit. Commit message is stored in commit's metadata. A good commit message consists of what has changed in this version and why it was changed.

**Advice:** You should commit your changes as frequently as possible. The creator of Linux kernel and Git, [Linus Torvalds](https://en.wikipedia.org/wiki/Linus_Torvalds), says if you need to use more than one sentence to describe what you just did, it is too many changes for one commit. That's because when you revert back to previous version (undo your changes), you lose too much of what you have done.

### Local version control systems (LVCS)

Local version control systems (LVCS) manage changes to files on a single user's local machine (computer). All versioned files and their history are stored on the user's local system. This means that changes are tracked and managed directly on the user's machine. (Unlike distributed version control systems or centralized version control system) LVCS lacks built-in mechanisms for collaboration among multiple users.

We can think of local version control systems (LVCS) as an offline word processor such as Microsoft Word. We can use it on our own, but we cannot collaborate with others. Collaboration can only occur through manual file sharing. If we want to collaborate, we have to send the files to our team members via email or other means.

*As for the other two version control systems, namely centralized version control systems (CVCS) and distributed version control systems (DVCS), broadly speaking we can think of them as an online word processor similar to Google Docs. We can share the link to our team members and our team members can see the latest changes as we sync the files, and make changes to those documents.*

In a nutshell, LVCS solve the problem of manually storing multiple copies (versions) of our files on a hard drive. The main disadvantage of Local Version Control Systems (LVCS) is that they don't facilitate easy collaboration.

![localVersionControlDiagram](https://imgur.com/QhdFtrw.png)

Examples of Local Version Control Systems:

- Source Code Control System (SCCS): One of the first version control systems, released in 1972, focused on source code. SCCS tracks changes and maintains file history. It is not maintained actively anymore and not recommended for use in new projects.

- RCS (Revision Control System): Released in 1982, it was meant to be an alternative to SCCS. Security is not not up to modern standards.

Early LVCS **operated only on single files** meaning they could not track an entire project/repository as an unit (also called an atomic commit).

**atomic commit:**
: Atomic commit treats changes to multiple files as one set. In an atomic commit if a commit involves changes to several files, all of changes are committed together successfully.

#### Why Atomic Commits Matter: A Practical Example

**With atomic commits.**

Imagine you have a project and you are using version control system to track/save different version of a project. Let's say the project is a book (you are writing a novel). There are separate files for each chapter.

You want to keep/store the archives of the project (book) at different times. Even though there are many files (chapters), these files are inherently connected to each other since they are a part of the same book.

After writing a few chapters, You decide to rename your protagonist from "Sarah" to "Emma" throughout the entire book. This change affects every chapter file, but conceptually, you're making one logical change: updating the character's name.
You modify all affected chapter files and commit them together with the message "rename protagonist to Emma." This is called an atomic commit.

If you later want to undo this change, one revert operation affects all files simultaneously, maintaining consistency across your entire project.

Essentially, in version control system that supports atomic commits, version control system keeps track of the entire project, and you can decide which files to include and not to include in each commit/archive.

**Without atomic commits.**

In version control systems that does not support atomic commits, each file has its own version history. One file might have 5 versions, another has 10 etc.

Using the above book example, if you want to change the name of the main character, you should save the new version of the each file separately.

To undo the name change later, you must remember to revert each file individually. It is both tedious and error-prone. You might accidentally miss reverting one chapter, leaving your story inconsistent.
