# Analyzing Linux User Activity Logs

![magnifier](https://i.imgur.com/WMAh4KL.jpeg)

If you want to analyze which users are logged in, how long they logged in, which commands they have executed etc., you can use below commands and methods.

## Login Logs

Login log files are stored in following locations:

- `/var/log/wtmp` – the login & logout history of users, as well as system boots and shutdowns.
- `/var/run/utmp` – currently logged in users.
- `/var/log/btmp` – failed login attempts.
- `/var/log/lastlog` - information about the last successful logins.

No need to check these log files manually. You can instead use below commands.

### who and w commands

**`who` :** prints information about users who are currently logged in.
`who` command uses `/var/run/utmp` file by default.

```txt
who

#username          #login time        #remote hostname/ip address
userX pts/0        2025-03-07 15:14   (111.111.33.111)
```

Usernames and the number of currently logged on users:

```txt
who -q

# usernames of currently logged in users
userX
userY

# the number of currently logged in users
users=2
```

`who` command can read logs from different logs files as well such as `/var/log/wtmp` file (it prints  the login history of users).

```shell
who /var/log/wtmp
```

More info on `who` command is [here](https://www.gnu.org/software/coreutils/manual/html_node/who-invocation.html#who_003a-Print-who-is-currently-logged-in).

<br>

**`w` command:** shows who is logged on and what they are doing.

```txt
w

15:33:21 up  6:33,  1 user,  load average: 0.00, 0.00, 0.00
USER     TTY        LOGIN@   IDLE   JCPU   PCPU WHAT
userX    pts/0      15:14    1.00s  0.02s  0.00s w
```

1. First line:
`15:33:21` => the current time
`up  6:33` => how long the system has been  running
`1 user` => how  many  users  are  currently logged on
`load average: 0.00, 0.00, 0.00` => the system load averages for the past 1, 5, and 15 minutes

2. Second line contains the headers
3. Third line shows following information:

   - login name
   - the tty name (name of the terminal session) or the remote host
   - login time
   - idle time
   - JCPU (the total time used by all processes attached to the particular terminal session)
   - PCPU (time used by the current process, named in the "WHAT" field)
   - the command line of their current process.

<br>

Show information about the specified user:

```bash
w <username>
```

Both `who` and `w` commands use `/var/run/utmp` file.

More info on `w` command can be found [here](https://manpages.ubuntu.com/manpages/jammy/man1/w.1.html).

<br>

### last, lastlog and lastb commands

#### last

`last` command shows a listing of last logged in (and logged out) users. `last` command uses `/var/log/wtmp` file.

Commands:

```bash
# show listing of last logged in users
last

# get login logs of a specific user
last <username>
```

eg:

```txt
last

# username, terminal, source IP address, start and stop time,      duration
userX    pts/0        111.111.33.111     Mon Feb 17 08:46          still logged in
reboot   system boot  0.0.0.0            Mon Feb 17 08:46          still running
userX    pts/1        111.11.111.69      Fri Jan 17 16:30 - 21:16  (04:46)
userX    pts/0        111.11.111.69      Fri Jan 17 14:01 - 16:38  (02:36)
reboot   system boot  0.0.0.0            Fri Jan 17 09:30 - 22:00  (12:30)
userX    pts/1        111.11.111.69      Thu Jan 30 11:47 - 15:01  (03:13)

wtmp begins Tue Aug  16 17:58:42 2023
```

Note: `reboot` is a pseudo  user. It indicates system reboot/restart, not an actual username.

Options:

Displaying the IP address in numbers-and-dots notation.

```txt
# without -i
last

userX    pts/1        login screen     Fri Jan 17 16:30 - 21:16  (04:46)
userX    pts/0        tty2     Fri Jan 17 14:01 - 16:38  (02:36)

# --------------------------------------------------
last -i

userX    pts/1        161.66.251.69     Fri Jan 17 16:30 - 21:16  (04:46)
userX    pts/0        161.66.251.69     Fri Jan 17 14:01 - 16:38  (02:36)
```

Specifying the number of lines to print.

```txt
# last -n
# eg: last -10
```

Print full login and logout times and dates.

```txt
# without -F option: Wed Feb  19 14:21 2025 - 15:41 (01:20)

last -F

# Wed Feb  19 14:21:00 2025 - Wed Feb  19 15:41:50 2025  (01:20)
```

More info on `last` and `lastb` commands can be found [here](https://manpages.ubuntu.com/manpages/focal/man1/last.1.html).

<br>

#### lastlog

`lastlog` command shows the most recent login of all users or of a given user.

`lastlog` command uses/prints the contents of the `/var/log/lastlog` file. The `lastlog` command results includes both regular user accounts and system accounts.

Note: `lastlog` prints only last login times, while `last` prints last log in and **log out** times along with system reboots and shutdowns.

```txt
lastlog

Username         Port     From             Latest
root             pts/1    -                 Wed Feb  19 14:17:58 +0900 2025
bin              **Never logged in**
daemon           **Never logged in**
adm              **Never logged in**
lp               **Never logged in**
sync             **Never logged in**
shutdown         **Never logged in**
halt             **Never logged in**
mail             **Never logged in**
```

Last login time of actual users who have logged in.

```txt
lastlog | grep -v "Never logged in"

Username         Port     From                 Latest
root             pts/1                         Wed Feb  19 14:17:58 +0900 2025
userX            pts/0    111.111.111.11       Fri Feb  14 15:14:18 +0900 2025
userP            pts/0    111.111.111.11       Thu Aug 15 21:55:30 +0900 2024
userY            pts/1    111.111.111.11       Wed Feb  19 14:11:46 +0900 2025
userT            pts/0    111.111.111.11       Fri Dec 13 13:57:46 +0900 2024
userK            pts/0    111.111.111.11       Fri Aug 23 10:26:19 +0900 2024
userJ            pts/2    111.111.111.11       Tue Feb 11 17:23:28 +0900 2025
```

Last login time of a specific user

```txt
lastlog -u <username>
```

More information on `lastlog` command can be found [here](https://manpages.ubuntu.com/manpages/trusty/man8/lastlog.8.html).

<br>

#### lastb

`lastb` works in the same way as `last` command. The difference is `lastb` prints all the bad login attempts. `lastb` command utilizes `/var/log/btmp` file. It is the same as using `last -f /var/log/btmp` command.

eg:

```txt
lastb

admin    ssh:notty    138.197.90.222   Mon Feb 17 08:47 - 08:48  (00:00)
support  ssh:notty    93.62.72.229     Mon Feb 17 08:46 - 08:47  (00:01)
support  ssh:notty    213.176.93.72    Mon Feb 17 08:46 - 08:46  (00:00)
```

You can see that some individuals tried to login to my server using above login names.

## Executed Command  history

### history command and .bash_history file

A history of each user's executed commands are stored in `home/<username>/.bash_history` file. There is `history` command as well that utilizes this `.bash_history` file.

A normal user can see only his/her own executed commands history, while a superuser can see all users' executed command history.

```txt
history

1  ls
2  history
3  ls -la
4  cat .bash_history
5  ls -la
6  history
```

The output is ordered from the oldest to latest executed commands.

Note: a user can delete/clear his or her `.bash_history` file.

More information on `history` command can be found [here](https://manpages.ubuntu.com/manpages/focal/man3/history.3tcl.html).

<br>

### acct & psacct

acct and psacct are packages targeting different linux distros, but function exactly the same.

Ubuntu/ Debian/ Linux Mint etc => acct
Fedora/ RHEL/ CentOS => psaact

These packages record information on users' activities such as login times and executed commands in `/var/log/pacct` file. Only the superuser can tamper with the log files created by these tools. The log files can be accessed by following commands:

- ac
- sa
- lastcomm
- dump-acct

In most cases `acct/psacct` is pre-installed and activated. Make sure it is switched on by running [`accton on`](https://manpages.ubuntu.com/manpages/trusty/man8/accton.8.html) command.

You can check if `acct/psacct` is installed by running `sudo systemctl status acct` commands.
In case it is not installed, you can install them using below instructions:
<details>
<summary>
Installing and enabling acct/psacct
</summary>
<div>

If `acct/psacct` is not pre-installed, they should be installed and activated using following commands depending on your linux distribution.

```sh
sudo apt install acct
# sudo dnf install psacct
```

Enable `acct/psacct`

```bash
sudo systemctl start acct
sudo systemctl enable acct
# sudo systemctl start psacct
# sudo systemctl enable psacct
```

Confirm `acct/psacct` is enabled

```bash
sudo systemctl status acct
```

</div>
</details>

<br>

#### ac

`ac` command prints statistics about users' connect time. It uses `/var/log/wtmp` file.

```txt
# ac -pd: print statistics about users' connect time (in hours) separated by day and username
# -d = daily-totals
# -p = individual-totals

sudo ac -pd

#day    #username    #daily total       #each user's total logged in time
        userX                            8.11
Jan 17  total        8.11
        userY                            0.02
        userX                            13.70
Jan  4  total       13.72
        userX                            2.53
        userZ                            0.15
Jan  5  total        2.68
        userX                            2.59
Jan  6  total        2.59

# on Jan 5th userX was logged in for 2.53 hours and userZ was logged in for 0.15hours.
# In total on Jan 5th all users were logged in for 2.68 hours.
```

Checking a certain user's connect/logged in time:

```sh
sudo ac <username>
```

More info on `ac` command can be found [here](https://manpages.ubuntu.com/manpages/trusty/man1/ac.1.html).

<br>

### sa

`sa` command summarizes information about previously executed commands as recorded in the `acct` file. `sa` command also creates files `savacct` (contains the number of times the command was called) and `usracct` (executed commandssummarized on a per-user basis).

```txt
sudo sa

#col1   #col2        #col3       #col4     #col5    #col6
16      0.01re       0.00cp      0avio     55344k   tail
10      0.00re       0.00cp      0avio     55584k   grep
9       0.00re       0.00cp      0avio     56464k   sort
9       0.00re       0.00cp      0avio     55344k   cat
9       0.00re       0.00cp      0avio     55344k   rmdir
9       0.00re       0.00cp      0avio       969k   ip
4       0.00re       0.00cp      0avio       661k   ac

# re: "elapsed time" in minutes
```

Column definitions:

- `#col1`: the number of times the command has been invoked (`tail` command was run 16 times)
- `col2`: elapsed time in minutes
- `col3`: CPU Time
- `col4`: the amount of time the command spent on I/O operations (e.g. reading from or writing to files or devices).
- `col5`: the amount of memory used by the command in kilobytes (kB).
- `col6`: executed command.

Print executed commands summary along with usernames.

```txt
suo sa -u

#username  #cpu time   #memory usage   #i/o time    #executed command
root       0.01 cpu    55648k mem      0 io         logger
root       0.00 cpu    55344k mem      0 io         rm
root       0.00 cpu      676k mem      0 io         sa
uxerX      0.00 cpu    58320k mem      0 io         sudo
uxerX      0.01 cpu    58064k mem      0 io         sudo
uxerX      0.00 cpu    55344k mem      0 io         tail
```

More information on `sa` command can be found [here](https://manpages.ubuntu.com/manpages/trusty/man8/sa.8.html).

<br>

### lastcomm

`lastcomm`: prints out information about previously executed commands.

```txt

sudo lastcomm

#command         #flag       #username       #terminal     #time the process started
mkdir                         root           __            0.00 secs Fri Feb  7 09:07
sudo             S            userX          pts/0         0.01 secs Fri Feb  7 09:07
sudo             F            userX          pts/1         0.00 secs Fri Feb  7 09:07
systemctl        S            root           pts/1         0.00 secs Fri Feb  7 09:07
ps               S            root           __            0.00 secs Fri Feb  7 09:07
sudo             S            userX          pts/0         0.00 secs Fri Feb  7 09:07
sudo             F            userX          pts/1         0.00 secs Fri Feb  7 09:07
systemctl        S            root           pts/1         0.00 secs Fri Feb  7 09:07
accton           S            root           __            0.00 secs Fri Feb  7 09:07
```

In terminal column `__`  means the command was run outside of an interactive session, possibly via a script or background process.

Flags:

- S: command executed by super-user
- F: command created a new (child) process
- C: command run in PDP-11 compatibility mode (an old hardware architecture)
- D: command terminated with the generation of a core file. It basically means while executing the command, the process crashed or encountered a serious error
- X: command was terminated with the signal SIGTERM
- no-flag: command was executed without any special conditions (like being superuser or generating a core dump)

Check commands executed by certain user:

```txt
sudo lastcomm --user userX

#command         #flag       #username        #terminal     #time the process started
tail                         userX pts/0      0.00 secs     Fri Feb  7 09:26
head                         userX pts/0      0.00 secs     Fri Feb  7 09:26
sudo             S           userX pts/0      0.00 secs     Fri Feb  7 09:26
tail                         userX pts/0      0.00 secs     Fri Feb  7 09:25
sudo             S           userX pts/0      0.01 secs     Fri Feb  7 09:25
head                         userX pts/0      0.01 secs     Fri Feb  7 09:25
tail                         userX pts/0      0.00 secs     Fri Feb  7 09:25
```

List records for specific commands:

```bash
sudo lastcomm --command shutdown
```

More information on `lastcomm` command can be found [here](https://manpages.ubuntu.com/manpages/trusty/man1/lastcomm.1.html).

<br>

### dump-acct

`dump-acct`: prints a list of all executed processes.
`acct`/`psacct` tools store data in `/var/account/pacct` file. The data stored in this file is not human readable. `dump-acct` command prints the contents of the `/var/account/pacct` file in an human readable format.

Eg:

```txt
sudo dump-acct /var/account/pacct

#command        #version   #user time  #system time   #effective time  #uid   #gid #memory        #io      #pid     #ppid     #time
accton          |v3|       0.00|       0.00|          1.00|            0|     0|     2628.00|     0.00|    2038|    2034|     |Mon Feb 10 09:24:18 2025
grep            |v3|       0.00|       0.00|          1.00|            0|     0|   222464.00|     0.00|    2039|    2034|     |Mon Feb 10 09:24:18 2025
cat             |v3|       0.00|       0.00|          1.00|            0|     0|   221376.00|     0.00|    2040|    2034|     |Mon Feb 10 09:24:18 2025
sh              |v3|       0.00|       0.00|          3.00|            0|     0|   222976.00|     0.00|    2034|    1967|     |Mon Feb 10 09:24:18 2025
curl            |v3|       0.00|       0.00|          1.00|            0|     0|   231744.00|     0.00|    2037|    2029|     |Mon Feb 10 09:24:18 2025
```

- Version: The version of the process accounting information.
- User time: The amount of time (in seconds) the CPU spent executing user code for the process.

- System time: The amount of time (in seconds) the CPU spent executing system calls on behalf of the process. This includes time spent in the kernel mode.

- Elapsed time: The total amount of real time (wall clock time) that passed while the process was running. This is the difference between the start and end times of the process.

- Effective time: The total time that the process was executing in user and system time. This is the sum of user time and system time.

- UID (User ID): The numeric user ID of the user who executed the command.
- GID: Group ID of the user who executed the command.
- Memory: The amount of memory (in kilobytes) used by the process during its execution.
- I/O: The number of input/output operations performed by the process.
- PID: Process ID
- PPID: Parent Process ID
- Time: start time

You can learn more about `dump-acct` command [here](https://manpages.ubuntu.com/manpages/focal/man8/dump-acct.8.html).

<br>

## auditd

auditd: The Linux Audit daemon.
[`auditd`](https://manpages.ubuntu.com/manpages/jammy/man8/auditd.8.html) is responsible for writing audit records to the disk. The records created by `auditd` are read/viewed by `aureport` and `ausearch` commands.

Make sure `auditd` is enabled by running `sudo systemctl status auditd`.

```txt
> sudo systemctl status auditd

auditd.service - Security Auditing Service
     Loaded: loaded (/usr/lib/systemd/system/auditd.service; enabled; preset: enabled)
     Active: active (running) since Mon 2025-02-10 09:24:18 JST; 8h ago
```

If `auditd` is not enabled, enable it by running `sudo auditd -s enable`.

The audit system can be configured and customized using [`auditctl` utility](https://manpages.ubuntu.com/manpages/jammy/man8/auditctl.8.html).

### ausearch

`ausearch` is a tool to query audit daemon logs.

Search for an event with either user ID.

```txt
sudo ausearch -i -au userX

----
type=USER_CMD msg=audit(01/10/25 16:05:25) : pid=14994 uid=userX auid=userX ses=4 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='cwd=/home/userX cmd=lastcomm exe=/usr/bin/sudo terminal=pts/2 res=success'
----
type=CRED_REFR msg=audit(01/10/25 16:05:25) : pid=14994 uid=userX auid=userX ses=4 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=PAM:setcred grantors=pam_env,pam_unix acct=root exe=/usr/bin/sudo hostname=? addr=? terminal=/dev/pts/2 res=success'
----
type=USER_CMD msg=audit(01/10/25 16:09:09) : pid=11052 uid=userX auid=userX ses=4 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='cwd=/home/userX cmd=history exe=/usr/bin/sudo terminal=pts/2 res=failed'
----
```

Pay attention to `type=USER_CMD` and `cmd=<command name>` records.

Meaning of the fields:

- type: The type of event
- msg=audit(timestamp:unique event ID):message identifier for the audit event
- pid: process ID that triggered the event
- uid:  user ID
- auid: audit user ID
- ses: session ID
- op: operation that was performed
- PAM (Pluggable Authentication Module): related to setting credentials (such as password or access tokens).
- acct: account affected by this operation or account hat executed this operation
- exe: executable that was run
- addr: IP address
- res: result of the operation
- com: name of the command

More info on `ausearch` can be found [here](https://manpages.ubuntu.com/manpages/jammy/man8/ausearch.8.html)

<br>

### aureport

`aureport` is a tool that produces summary reports of audit daemon logs.

`aureport` uses the same log files as `ausearch`, the difference is it generates formatted summaries of the events. It is possible to specify the even types using below options.

Some of the options:

- `-au`: Report about authentication attempts
- `--comm`: Report about commands run
- `-l`: Report about logins
- `-m`: Report about account modifications
- `-n`: Report  about  anomaly  events
- `-u`: Report about users

```txt
sudo aureport -i --comm

Command Report
=================================================
# date      time     comm  term  host auid event
=================================================
1. 02/23/23 17:42:30 systemd ? ? unset 22286
2. 02/23/23 17:42:30 systemd ? ? unset 22287
3. 02/23/23 17:43:35 systemd ? ? unset 22373
4. 02/23/23 17:43:35 systemd ? ? unset 22374
5. 02/23/23 17:44:47 systemd ? ? unset 22473
6. 02/23/23 17:44:47 systemd ? ? unset 22474
7. 02/23/23 17:45:55 systemd ? ? unset 22585
8. 02/23/23 17:45:55 systemd ? ? unset 22586
9. 02/23/23 17:47:01 systemd ? ? unset 22712
```

Column definitions:

- `#` : record number
- `comm`: command name
- `term` terminal name
- `auid`: user ID
- `event`: event ID

```txt
suo aureport -i -u

User ID Report
====================================================================
#        date     time    auid  term    host  exe          event
====================================================================
109147. 01/12/24 09:12:04 userX /dev/pts/0 ? /usr/bin/sudo 456
109148. 01/12/24 09:12:04 userX /dev/pts/0 ? /usr/bin/sudo 457
109149. 01/12/24 09:12:04 userX /dev/pts/0 ? /usr/bin/sudo 458
109150. 01/12/24 09:12:04 userX /dev/pts/0 ? /usr/bin/sudo 459
109151. 01/12/24 09:12:19 userX /dev/pts/0 ? /usr/bin/sudo 460
109152. 01/12/24 09:12:19 userX pts/0      ? /usr/bin/sudo 461
109153. 01/12/24 09:12:19 userX /dev/pts/0 ? /usr/bin/sudo 462
109154. 01/12/24 09:12:19 userX /dev/pts/0 ? /usr/bin/sudo 463
```

More info on `aureport` can be found [here](https://manpages.ubuntu.com/manpages/jammy/man8/aureport.8.html).

----

## Logrotate

[logrotate](https://manpages.ubuntu.com/manpages/xenial/man8/logrotate.8.html)  is  designed  to  ease administration of systems that generate large numbers of log files.  It allows automatic rotation, compression, removal, and mailing of log files.

Basically logrotate crates a new log file while archiving/copying an existing log file and keeping it for specified period of time before deleting it. In most linux distros lograte is set to execute on a weekly basis.

You can specify the frequency of the logrotate execution for each type of the logfile and retention period of the achrived logs using `/etc/logrotate.conf` file.

`/etc/logrotate.conf` file:

```txt
# see "man logrotate" for details

# global options do not affect preceding include directives

# rotate log files weekly
weekly

# keep 4 weeks worth of backlogs
rotate 4

# create new (empty) log files after rotating old ones
create

# use date as a suffix of the rotated file
dateext

# uncomment this if you want your log files compressed
#compress

# packages drop log rotation information into this directory
include /etc/logrotate.d

# system-specific logs may also be configured here.
```

You can specify rules for each type of the log files.
eg:

```txt
/var/log/httpd/access.log {
           rotate 5
           weekly
           postrotate
               /usr/bin/killall -HUP syslogd
           endscript
       }
```
