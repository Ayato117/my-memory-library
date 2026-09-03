document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');
    
    signupForm.addEventListener('submit', function(event) {
        const password = document.getElementById('signup-password').value;
        const repeatPassword = document.getElementById('signup-repeat-password').value;

        if (password !== repeatPassword) {
            alert('パスワードが一致しません。');
            event.preventDefault(); // フォームの送信を防ぐ
        }
    });
});
