function show_save_result (data) {
	if (data.result == 'ok') {
		document.getElementById('save_result').innerText = 'Save Successful';
	} else {
		document.getElementById('save_result').innerText = 'Save Failed';
	}
}
	
function submit_change(id) {
	first_name = document.getElementById('first_name_' + id).value
	surname = document.getElementById('surname_' + id).value

	fetch('change_user_details.php', {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ 'id': id, 'first_name': first_name, 'surname': surname })
	}
	)
	.then((response) => response.json())
	.then((data) => show_save_result(data));
}

function populate_form() {
	var xhr= new XMLHttpRequest();
	xhr.open('GET', 'get_user_data.php', true);
	xhr.onreadystatechange= function() {
		if (this.readyState!==4) {
			return;
		}
		if (this.status!==200) {
			return;
		}
		const users = JSON.parse (this.responseText);
		table_body = document.getElementById('user_table').getElementsByTagName('tbody')[0];
		users.forEach(updateTable);

		function updateTable (user) {
			var row = table_body.insertRow(0);
			var cell0 = row.insertCell(-1);
			cell0.appendChild(document.createTextNode(user['user_id']));
			var userId = document.createElement('input');
			userId.type = 'hidden';
			userId.id = 'user_id_' + user['user_id'];
			userId.name = 'user_id';
			userId.value = user['user_id'];
			cell0.appendChild(userId);
			var cell1 = row.insertCell(1);
			var firstName = document.createElement('input');
			firstName.type = 'text';
			firstName.id = 'first_name_' + user['user_id'];
			firstName.name = 'first_name';
			firstName.value = user['first_name'];
			cell1.appendChild(firstName);
			var cell2 = row.insertCell(2);
			var surname = document.createElement('input');
			surname.type = 'text';
			surname.id = 'surname_' + user['user_id'];
			surname.name = 'surname';
			surname.value = user['surname'];
			cell2.appendChild(surname);
			var cell3 = row.insertCell(3);
			var button = document.createElement('input');
			button.type = 'button';
			button.value = 'Update';
			button.addEventListener('click', function () { submit_change(user['user_id']); });
			cell3.appendChild(button);
		}
	};
	xhr.send();
}
