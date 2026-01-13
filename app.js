(function () {
  var form = document.querySelector('.task-form');
  var input = document.getElementById('task-input');
  var list = document.getElementById('task-list');
  var count = document.getElementById('task-count');

  var tasks = [];

  function updateCount() {
    count.textContent = String(tasks.length);
  }

  function createTaskElement(task) {
    var item = document.createElement('li');
    item.className = 'task-item';

    var label = document.createElement('label');
    label.className = 'task-item__label';

    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'task-item__checkbox';
    checkbox.checked = task.done;

    var text = document.createElement('span');
    text.className = 'task-item__text';
    text.textContent = task.label;

    var remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'task-item__remove';
    remove.textContent = '削除';

    label.appendChild(checkbox);
    label.appendChild(text);
    item.appendChild(label);
    item.appendChild(remove);

    if (task.done) {
      item.className += ' task-item--done';
    }

    checkbox.addEventListener('change', function () {
      task.done = checkbox.checked;
      if (task.done) {
        if (item.className.indexOf('task-item--done') === -1) {
          item.className += ' task-item--done';
        }
      } else {
        item.className = item.className.replace(' task-item--done', '');
      }
    });

    remove.addEventListener('click', function () {
      list.removeChild(item);
      tasks = tasks.filter(function (current) {
        return current !== task;
      });
      updateCount();
    });

    return item;
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var value = input.value.trim();
    if (!value) {
      return;
    }

    var task = {
      label: value,
      done: false
    };

    tasks.push(task);
    list.appendChild(createTaskElement(task));
    input.value = '';
    updateCount();
  });

  updateCount();
})();
