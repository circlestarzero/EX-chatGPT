function get(selector, root = document) {
  return root.querySelector(selector);
}
const newChatBtn = get(".new-chat");
const sidebarList = get(".sidebar-list");
const sidebar = get(".sidebar")
function fetchChatLists() {
  fetch('/api/chatLists')
    .then(response => response.json())
    .then(data => {
      if (data.hasOwnProperty('chatLists')) {
        console.log(data)
        data.chatLists.forEach(message => {
          NewChat(message.chatName, message.uuid);
          sidebar.scrollTop = sidebar.scrollHeight;
        });
      }
    })
    .catch(error => console.error(error));
}
fetchChatLists();
function formatChatDate(date) {
  const M = "0" + (date.getMonth() + 1);
  const D = "0" + date.getDate();
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();
  return `${M.slice(-2)}/${D.slice(-2)} ${h.slice(-2)}:${m.slice(-2)}`;
}
function generateUUID() {
  // Generate a random UUID
  // Adapted from https://stackoverflow.com/a/2117523/7049894
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
function NewChat(ChatName, uuid) {
  if (ChatName == null) {
    ChatName = 'New Chat ' + formatChatDate(new Date())
  }
  const newChatItem = `
    <li class="chat-list">
        <a class="chat-list-wrap">
          <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round"
            stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <div class="chat-list-text">${ChatName}</div>
          <div class="absolute flex right-1 z-10 text-gray-300 visible">
            <button class="edit-button">
              <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round"
                stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 20h9"></path>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
              </svg>
            </button>
            <button class="delete-button">
              <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round"
                stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
            </button>
          </div>
        </a>
      </li>
    `
  if (uuid == null) {
    uuid = generateUUID();
  }
  sidebarList.insertAdjacentHTML('afterbegin', newChatItem);
  sidebarList.firstElementChild.setAttribute('uuid', uuid);
  deleteButton = sidebarList.firstElementChild.querySelector(".delete-button");
  console.log(sidebarList.firstElementChild.getAttribute('uuid'));
  const chatList = deleteButton.closest('.chat-list');
  deleteButton.addEventListener('click', function () {
    setChatLists();
    const chatLists = document.querySelectorAll('.chat-list');
    if (chatLists.length > 1) {
      chatList.remove();
    }
  });
  const editButton = chatList.querySelector('.edit-button');
  editButton.addEventListener('click', function () {
    const chatListText = editButton.parentNode.parentNode.querySelector('.chat-list-text')
    console.log(chatListText)
    chatListText.contentEditable = true;
    chatListText.focus = true;
    chatListText.setAttribute('spellcheck') = false;
  });
  const chatListText = chatList.querySelector('.chat-list-text')
  chatListText.contentEditable = false;
  chatList.addEventListener('blur', function () {
    chatListText.contentEditable = false;
  });
  chatList.addEventListener('click', function () {
    chatListParent = chatList.parentNode;
    if (chatListParent) {
      if(chatListParent.firstElementChild == chatList) return;
      chatListParent.insertBefore(chatList, chatListParent.firstElementChild);
      loadHistory();
      setChatLists();
    }
  });
}
newChatBtn.addEventListener("click", function () {
  NewChat(null, null);
  loadHistory();
  setChatLists();
});
const deleteButtons = document.querySelectorAll('.delete-button');
deleteButtons.forEach((deleteButton) => {
  deleteButton.addEventListener('click', function () {
    const chatList = deleteButton.closest('.chat-list');
    const chatLists = document.querySelectorAll('.chat-list');
    if (chatLists.length > 1) {
      setChatLists();
      chatList.remove();
    }
  });
});
const editButtons = document.querySelectorAll(".edit-button");
editButtons.forEach((editButton) => {
  editButton.addEventListener('click', function () {
    const chatListText = editButton.parentNode.parentNode.querySelector('.chat-list-text')
    console.log(chatListText)
    chatListText.contentEditable = true;
    chatListText.focus = true;
  });
});
const chatListTexts = document.querySelectorAll('.chat-list-text');
chatListTexts.forEach((chatListText) => {
  chatListText.contentEditable = false;
  chatListText.addEventListener('blur', function () {
    chatListText.contentEditable = false;
  });
});

function setChatLists() {
  lists = [];

  // Convert the JavaScript object to a JSON string
  chatLists = document.querySelectorAll('.chat-list');
  chatLists.forEach((chatList) => {
    const uuid = chatList.getAttribute('uuid');
    const name = chatListText = chatList.querySelector('.chat-list-text').textContent
    lists.push({ "uuid": uuid, "chatName": name })
  })
  const chatListJSON = {
    "chatLists": lists
  };
  console.log(chatListJSON)
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(chatListJSON)
  };
  fetch('/api/setChatLists', options)
    .then(response => {
      if (response.ok) {
        return response.ok;
      } else {
        throw new Error('Failed to send data to server');
      }
    })
    .then(data => {
      console.log('Server response:', data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}
