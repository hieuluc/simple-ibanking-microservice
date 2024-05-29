document.addEventListener('DOMContentLoaded', function () {
  const accessToken = sessionStorage.getItem('token');
  if (!accessToken) {
    window.location.href = 'login.html';
  } else {
    let username;
    // Lấy thông tin người dùng bằng token
    fetch('http://localhost:8005/user/me', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }).then(response => response.json())
      .then(data => {
        username = data.username;
        document.getElementById('payerName').value = data.full_name;
        document.getElementById('payerEmail').value = data.email;
        document.getElementById('payerPhone').value = data.phone;
        // Lấy lịch sử giao dịch
        fetchHistory(data.username, accessToken);
        // Lấy số dư tài khoản
        fetch(`http://localhost:8005/get-balance/${data.username}`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }).then(response => response.json())
          .then(data => {
            document.getElementById('availableBalance').value = data.bal;
          })
          .catch(() => {
            window.location.href = 'login.html';
          });
      })
      .catch(() => {
        window.location.href = 'login.html';
      });

    // Đăng xuất
    document.getElementById('signout').addEventListener('click', function () {
      sessionStorage.removeItem('token');
      window.location.href = 'login.html';
    });

    // Tự động cập nhật thông tin học phí khi nhập mã sinh viên
    document.getElementById('studentID').addEventListener('input', function () {
      const studentID = this.value;
      fetchStudentInfo(studentID, accessToken);
    });

    // Mở nút xác nhận khi đồng ý điều khoản và học phí nhỏ hơn số dư
    checkBox = document.getElementById("terms");
    checkBox.addEventListener('change', function () {
      const tuition_fee = parseFloat(document.getElementById("tuitionAmount").value);
      const available_balance = parseFloat(document.getElementById("availableBalance").value);
      if (checkBox.checked && tuition_fee < available_balance) {
        document.querySelector('button[type="submit"]').disabled = false;
      } else if (!checkBox.checked || tuition_fee > available_balance) {
        document.querySelector('button[type="submit"]').disabled = true;
      }
    });

    // Gửi OTP và mở modal xác nhận OTP khi nhấn nút Xác nhận
    var confirmButton = document.querySelector('button[type="submit"]');
    let version;
    confirmButton.addEventListener("click", function (event) {
      event.preventDefault(); // Ngăn không submit form
      var otpModal = new bootstrap.Modal(document.getElementById('otpModal'), {
        keyboard: false
      });
      const receiver = document.getElementById('studentID').value;
      fetch(`http://localhost:8005/process-tuition/?username=${encodeURIComponent(username)}&receiver=${encodeURIComponent(receiver)}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
      }).then(response => {
        if (!response.ok) {
          response.json().then(data => alert(data.detail))
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      }).then(data => {
        otpModal.show();
        version = data.version;
        alert('OTP has been sent.');
      }).catch(error => {
        console.error('There was an error!', error); // Xử lý lỗi nếu có
      });
    });

    // Gửi lại OTP khi nhấn nút Gửi lại
    document.getElementById('sendOTP').addEventListener('click', function () {
      fetch(`http://localhost:8005/send-otp/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          receiver_email: document.getElementById('payerEmail').value
        })
      }).then(response => {
        if (!response.ok) {
          response.json().then(data => alert(data.detail))
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      }).then(data => {
        alert(data.detail);
      }).catch(error => {
        console.error('There was an error!', error); // Xử lý lỗi nếu có
      });
    });

    // Xác thực OTP và xử lý thanh toán
    document.getElementById('otpForm').addEventListener('submit', function (event) {
      event.preventDefault();
      fetch(`http://localhost:8005/verify-and-process-payment/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          version: version,
          otp: document.getElementById('otpCode').value,
          username: username,
          email: document.getElementById('payerEmail').value,
          receiver: document.getElementById('studentID').value,
          amount: document.getElementById('tuitionAmount').value
        })
      }).then(response => {
        if (!response.ok) {
          response.json().then(data => alert(data.detail))
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      }).then(data => {
        alert(data.message);
        // Sau khi xác nhận thành công, đóng modal và kết thúc quy trình thanh toán
        $('#otpModal').modal('hide');
        location.reload();
      }).catch(error => {
        console.error('There was an error!', error); // Xử lý lỗi nếu có
      });
    });

  }
});

// Hàm lấy thông tin học phí
function fetchStudentInfo(studentID, accessToken) {
  const apiUrl = `http://localhost:8005/tuition/${studentID}`;

  fetch(apiUrl, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.fee_paid) {
        // Nếu học phí đã được thanh toán, hiển thị thông báo
        alert("This student has already paid the tuition fee.");
      } else {
        // Nếu chưa thanh toán, cập nhật thông tin vào form
        document.getElementById('studentName').value = data.full_name;
        document.getElementById('tuitionAmount').value = data.tuition_fee;
        if (data.tuition_fee < document.getElementById('availableBalance').value && document.getElementById("terms").checked == true) {
          document.querySelector('button[type="submit"]').disabled = false;
        } else {
          document.querySelector('button[type="submit"]').disabled = true;
        }
      }
    })
    .catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
    });
}

function fetchHistory(username, accessToken) {
  fetch(`http://localhost:8005/history/${username}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      // Lấy tham chiếu đến UL element
      let transactionList = document.getElementById('transactionList');
      // Xóa danh sách hiện tại để tránh trùng lặp
      transactionList.innerHTML = '';
      // Duyệt qua mảng data và tạo li elements
      data.forEach(transaction => {
        let listItem = document.createElement('li');
        listItem.classList.add('list-group-item');
        // Format vnd
        let formattedAmount = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(transaction.amount);
        // Đặt nội dung cho listItem
        listItem.textContent = `Giao dịch: ${formattedAmount} - Người nhận: ${transaction.receiver} - Ngày: ${new Date(transaction.date)}`;
        // Thêm listItem vào transactionList
        transactionList.appendChild(listItem);
      });
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
}
