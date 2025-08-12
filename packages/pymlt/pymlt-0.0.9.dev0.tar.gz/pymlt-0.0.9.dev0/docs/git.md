# git

https://www.datacamp.com/courses/introduction-to-git  
https://www.atlassian.com/git/tutorials  

### chapter 1 - basic workflow

`git status` return files that have differences between local and remote  

`git diff` checks diff between current and last saved version  
`git diff (filename)` checks diff of specific file  
`git diff (directory)` checks diff of specific directory  

`git stash` stash changes without commit  
`git stash save (message)` stashes changes with message  
`git stash list` lists all stashed changes  
`git stash pop` reapplies changes to current branch  

`git diff -r HEAD` checks diff of revision (-r)  
`git diff -r HEAD (path)` checks diff of file  

`git commit` will prompt default editor for message  
`git commit -m (message)`  adds mess  
`git commit --amend (message)` corrects commit message  

`git log` = check earlier commits / use space bar to go down a page, use q to quit  
`git log -3` = show 3 latest  
`git log (path)` = check specific file

### chapter 2 - repositories

`git log` shows commits + unique hash  
`git show (6 first characters of hash)` show details of commit  

`git show HEAD` = most recent commit  
`git show HEAD~1` = the one before the most recent one  

`git blame` shows who made changes to each line of the files  
`git annotate (file)` shows who made changes to each line of the file  

`git diff HEAD~1..HEAD~3` shows diff between state  
`git diff abc123..def456` shows diff between commits  

`git add (file)` adds untracked file  
`git add .` adds all untracked files  

`git clean -n` identifies untracked files  
`git clean -f` deletes untracked files  

`git config --list --system` = every user  
`git config --list --global` = every project  
`git config --list --local` = specific project  

`git config --global user.name (name)` sets user name  
`git config --global user.email (email)` sets user email address  
`git config --global pager.branch false` sets output less verbose  
`git config --global core.editor "nano"` sets default editor  

### chapter 3 - undo

`git add .` adds all files to staging area  
`git reset` unstage all files  
`git reset file` unstage file  
`git reset HEAD file` unstages file  

`git checkout -- file` = overwrite changed local file from file in staging area  
`git checkout (hash) file` = overwrite local file from specific commit

`git checkout -- directory` = overwrite all files in directory  
`git checkout -- .` = dot is referring to current directory  

`git rm file` = remove file and commit removal  

### chapter 4 - branches

`git branch` returns all branches; * indicates branch you are in  
`git branch (branch)` create a new branch  
`git branch -d (branch)` deletes branch  

`git checkout (branch)` moves to new branch  
`git checkout -b (branch)` creates and moves to new branch  

`git diff (branch)..(branch)` shows difference between two branches  
`git merge (branch)` merges branch with current branch    
`git merge --squash (branch)` merges branch and squashes all commits  

### chapter 5 - collaborating

`git init (repo)` creates a new repo  
`git init (path)` turns existing folder into repo  

`git clone (url)` clones from remote  
`git clone (path)` clones from local  
`git clone (path) (repo)` clones and rename from local  

`git remote -v` returns location or origin of repo, -v for verbose  
`git remote add origin (url)` adds an extra remote repo  
`git remote add origin (path)` adds an extra local repo  
`git remote rm origin` removes remote repo  

`git fetch` fetches metadata from remote to local  
`git pull` pulls all updates from remote to local  
`git pull origin (branch)` pulls updates on master from origin to local  
`git push origin (branch)` pushes updates to origin  
