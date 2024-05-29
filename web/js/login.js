document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const url = 'http://localhost:8005/token';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        alert('Login failed!');
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log('Token:', data.access_token);
        // Lưu token vào sessionStorage/localStorage hoặc cookie tùy theo yêu cầu
        sessionStorage.setItem('token', data.access_token);
        // Chuyển hướng sang trang home
        window.location.href = 'index.html';
    })
    .catch(error => console.error('Error:', error));
});
