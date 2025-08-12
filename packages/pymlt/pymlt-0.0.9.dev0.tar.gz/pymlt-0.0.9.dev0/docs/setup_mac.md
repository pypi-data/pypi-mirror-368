# notes

## getting started on a mac

- [brew](https://brew.sh)
- [mac setup](https://sourabhbajaj.com/mac-setup/)


## terminal

- Background colour black + opacity 75%
- Check 'Inactive window'
- Vertical cursor

<kbd>CMD</kbd> + <kbd>l</kbd> = clear previous output <br>
<kbd>CMD</kbd> + <kbd>k</kbd> = clear all output <br>
<kbd>↑</kbd> = previous command <br>


## install

- install Xcode
- install zsh
- install [brew](https://brew.sh)
- install brew > python
- install brew > gh
- install atom

```bash
# tree
brew install tree
tree -L 1 # depth of 1
```

## zsh

- [ohmyzsh](https://ohmyz.sh)
- [calmcode](https://calmcode.io/zsh/introduction.html)
- [zsh cheatsheet](https://github.com/ohmyzsh/ohmyzsh/wiki/Cheatsheet)

```bash
# abbreviations
alias | grep "git"
gb = git branch
gco = git checkout
gst = git status

# set print to terminal
git config --global pager.branch false

```


```bash
# open config file
atom .zshrc

# enter alias
alias gitwip="git add . && git commit -m wip && git push"
alias lab="jupyter lab"
```



## git

- [tutorial](https://github.com/firstcontributions/first-contributions)

```bash
# config user
git config --global user.name "Ben van Vliet"
git config --global user.email "benvliet@icloud.com"

# config output
git config --global pager.branch false
````



python3 -m venv env
source env/bin/activate
pip install pandas
deactivate

```bash
#initialize a git repo
git init
# add remote repo
git remote add origin https://github.com/user/repo.git
# set upstream branch
git push -u origin master
````

```bash
# fetch meta data, no file transfer
git fetch

# pull latest changes
git pull
```




```bash
# --porcelain is machine interpretable output
git blame README.md --porcelain | grep  "^author " | sort -u
```

```bash
# zsh alias
alias | grep "git"

# examples
gb = git branch
gco = git checkout
gst = git status
```

## gh actions

- [udemy → actions](https://www.udemy.com/course/github-actions/)
- [examples](https://github.com/sdras/awesome-actions)


## gh cli

[gh cli](https://cli.github.com)

```bash
# list all repos
gh repo list

# clone repo
gh repo clone benvliet/notes

# issues
gh issue list
gh issue list --repo benvliet/notes
gh issue view 1
gh issue create
```


## py

```bash
# create venv
python3 -m venv env
# activate
source env/bin/activate
# pip freeze
# pip install
# pip uninstall

```

https://google.github.io/styleguide/pyguide.html



