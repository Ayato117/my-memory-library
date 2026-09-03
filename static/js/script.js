document.addEventListener("DOMContentLoaded", function() {
    
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const sidebar = document.querySelector('.sidebar');
  
    hamburgerMenu.addEventListener('click', function() {
      // ハンバーガーメニューがアクティブかどうかをトグルする
      hamburgerMenu.classList.toggle('active');
      sidebar.classList.toggle('active');
    });
});
