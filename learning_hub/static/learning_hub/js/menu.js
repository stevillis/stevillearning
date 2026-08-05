document.addEventListener("DOMContentLoaded", () => {
  const main = document.querySelector("main");
  const footer = document.querySelector("footer");
  const hamburgerMenu = document.querySelector(".hamburger-menu");
  const mobileMenu = document.querySelector(".mobile-menu");
  const headerContent = document.querySelector(".header-content");

  hamburgerMenu.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });

  main.addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
  });

  footer.addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
  });

  headerContent.addEventListener("click", (event) => {
    if (!event.target.classList.contains("hamburger-menu"))
      mobileMenu.classList.add("hidden");
  });
});
