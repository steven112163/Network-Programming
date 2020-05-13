#!/bin/bash

SERVER_IP=$1
SERVER_PORT=$2
SESSION="hw3_test"
SLEEP_TIME=0.5
if [ -z ${SERVER_IP} ] || [ -z ${SERVER_PORT} ]; then
  echo "Usage: $0 <server ip> <server port>"
  exit 1
fi

if [ -n "$(tmux ls | grep ${SESSION})" ]; then
  tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION
tmux set remain-on-exit on

tmux select-pane -t 0
tmux split-window -v
tmux split-window -h

tmux select-pane -t 0
tmux split-window -h

# cat testcase |
# while IFS= read data
# do
#     tmux send-keys -t 0 "$data" Enter
#     sleep 1
# done

sleep 2.5
echo "Connection test"
for i in $(seq 0 3); do
  tmux send-keys -t ${i} "python3 ./client.py ${SERVER_IP} ${SERVER_PORT}" Enter
  sleep 0.5
done

echo "Registration test"
for i in $(seq 0 3); do
  # register successfully
  tmux send-keys -t ${i} "register user${i} user${i}@qwer.zxcv user${i}" Enter
  sleep $SLEEP_TIME
  # show already used
  tmux send-keys -t ${i} "register user${i} user${i}@qwer.zxcv user${i}" Enter
  sleep $SLEEP_TIME
  # command format incorrect
  tmux send-keys -t ${i} "register user${i} user${i}@qwer.zxcv" Enter
  sleep $SLEEP_TIME
  # show login failed
  tmux send-keys -t ${i} "login user${i}" Enter
  sleep $SLEEP_TIME
done

echo "Functions test"
index=0
for tc in qwer asdf zxcv qwer; do
  # types wrong account and password
  tmux send-keys -t ${index} "login ${tc} ${tc}" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "whoami" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "logout" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "create-board NP_HW" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "create-post NP_HW --title About NP HW_${index} --content Help!<br>I have some problems!" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "delete-post ${index}" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "update-post ${index} --title NP HW_${index}" Enter
  sleep $SLEEP_TIME
  # show login first
  tmux send-keys -t ${index} "comment ${index} Ha! ha! ha!" Enter
  sleep $SLEEP_TIME

  # types correct account and password
  tmux send-keys -t ${index} "login user${index} user${index}" Enter
  sleep $SLEEP_TIME
  # show logout first
  tmux send-keys -t ${index} "login user${index} user${index}" Enter
  sleep $SLEEP_TIME
  # show username
  tmux send-keys -t ${index} "whoami" Enter
  sleep $SLEEP_TIME
  # show bye message
  tmux send-keys -t ${index} "logout" Enter
  sleep $SLEEP_TIME
  index=$((index + 1))
done

echo "Board test"
for i in $(seq 0 3); do
  # types correct account and password
  tmux send-keys -t ${i} "login user${i} user${i}" Enter
  sleep $SLEEP_TIME
  # create board successfully
  tmux send-keys -t ${i} "create-board NP_HW${i}" Enter
  sleep $SLEEP_TIME
  # show board exists
  tmux send-keys -t ${i} "create-board NP_HW${i}" Enter
  sleep $SLEEP_TIME
  # create-board format incorrect
  tmux send-keys -t ${i} "create-board" Enter
  sleep $SLEEP_TIME
  # list all boards
  tmux send-keys -t ${i} "list-board" Enter
  sleep $SLEEP_TIME
  # list all boards with key word
  tmux send-keys -t ${i} "list-board ##${i}" Enter
  sleep $SLEEP_TIME
done

echo "Post create and list test"
for idx in $(seq 0 3); do
  i=$((3 - idx))
  # create post successfully
  tmux send-keys -t ${i} "create-post NP_HW${i} --title About NP HW_${i}4 --content Help!<br>I have some problems!" Enter
  sleep $SLEEP_TIME
  tmux send-keys -t ${i} "create-post NP_HW${i} --title About NP HW_${i}5 --content Help!<br>I have some problems!" Enter
  sleep $SLEEP_TIME
  # show board does not exist
  tmux send-keys -t ${i} "create-post NP_HW --title About NP HW_${i} --content Help!<br>I have some problems!" Enter
  sleep $SLEEP_TIME
  # create-post format incorrect
  tmux send-keys -t ${i} "create-post NP_HW" Enter
  sleep $SLEEP_TIME
  # list all posts
  tmux send-keys -t ${i} "list-post NP_HW${i}" Enter
  sleep $SLEEP_TIME
  # list all posts with key word
  tmux send-keys -t ${i} "list-post NP_HW${i} ##${i}" Enter
  sleep $SLEEP_TIME
  # show board does not exist
  tmux send-keys -t ${i} "list-post NP_HW" Enter
  sleep $SLEEP_TIME
done

echo "Post update and delete test"
for idx in $(seq 0 3); do
  i=$((3 - idx))
  # show update successfully
  post=$((idx * 2 + 1))
  tmux send-keys -t ${i} "update-post ${post} --title About NP HW_${i}4${i}" Enter
  sleep $SLEEP_TIME
  tmux send-keys -t ${i} "update-post ${post} --content Help me!<br>I have some problems!" Enter
  sleep $SLEEP_TIME
  # show post does not exist
  tmux send-keys -t ${i} "update-post 888 --title test" Enter
  sleep $SLEEP_TIME
  # update-post format incorrect
  tmux send-keys -t ${i} "update-post 888" Enter
  sleep $SLEEP_TIME
  # show delete successfully
  post=$((i * 2 + 2))
  tmux send-keys -t ${i} "delete-post ${post}" Enter
  sleep $SLEEP_TIME
  # show post does not exist
  tmux send-keys -t ${i} "delete-post 888" Enter
  sleep $SLEEP_TIME
  # delete-post format incorrect
  tmux send-keys -t ${i} "delete-post" Enter
  sleep $SLEEP_TIME

  tmux send-keys -t ${i} "logout" Enter
  sleep $SLEEP_TIME
done

echo "Switch users and comment"
for i in $(seq 0 3); do
  idx=$((3 - i))
  tmux send-keys -t ${idx} "login user${i} user${i}" Enter
  sleep $SLEEP_TIME
  tmux send-keys -t ${idx} "whoami" Enter
  sleep $SLEEP_TIME

  post=$((i * 2 + 1))
  # show not the owner
  tmux send-keys -t ${idx} "delete-post ${post}" Enter
  sleep $SLEEP_TIME
  # show not the owner
  tmux send-keys -t ${idx} "update-post ${post} --title test" Enter
  sleep $SLEEP_TIME
  # comment successfully
  tmux send-keys -t ${idx} "comment ${post} Ha! ha! ha!" Enter
  sleep $SLEEP_TIME
  # show post does not exist
  tmux send-keys -t ${idx} "comment 888 Ha! ha! ha!" Enter
  sleep $SLEEP_TIME
  # read successfully
  tmux send-keys -t ${idx} "read ${post}" Enter
  sleep $SLEEP_TIME
  # show post does not exist
  tmux send-keys -t ${idx} "read 888" Enter
  sleep $SLEEP_TIME

  tmux send-keys -t ${idx} "logout" Enter
  sleep $SLEEP_TIME
  tmux send-keys -t ${idx} "exit" Enter
  sleep $SLEEP_TIME
done

echo "Show result."
sleep 3
tmux attach-session -t $SESSION
