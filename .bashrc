# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=


# Paths
export MY_STORAGE="/scratch/mingchiehhu"


# Alias
alias ll='ls -alF'
alias la='ls -A'
alias ls='ls --color=auto'
alias l='ls -rtlh --full-time --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias src='source ~/.bashrc'

## Slurm helpers
alias interactive='srun --pty --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=8G --time=1:00:00 bash'
alias st='sacct --format=JobID,JobName%30,State,Elapsed,Timelimit,AllocNodes,Priority,Start,NodeList'
alias sq="squeue -u $USER --format='%.18i %.12P %.30j %.15u %.2t %.12M %.6D %R'"
alias slurm-show-my-accounts='sacctmgr list user "$USER" withassoc format="user%-20,account%-45,maxjobs,maxsubmit,maxwall,maxtresperjob%-40"'
alias slurm-show-all-accounts='sacctmgr show account format=Account%30,Organization%30,Description%60'
alias slurm-show-nodes='sinfo -lNe'

# Shellstyle

## Assuming your shell background is black!

## Prompt setting (readable prompt colors and username@hostname:)
export PS1='\[\033[01;32m\]\u@\h\[\033[0m\]:\[\033[01;34m\]\w\[\033[0m\]\$ '
LS_COLORS='di=01;34:ln=01;36:ex=01;32:*.tar=01;31:*.zip=01;31'