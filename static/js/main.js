const btnDelete = document.querySelectorAll(".btn-delete");

if(btnDelete){
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) =>{
        btn.addEventListener("click", (e) =>{
            if(!confirm("Are you sure you want to delete it?")){
                e.preventDefault();
            }
        })
    })
}

const btnSwitch = document.querySelector("#switch");

btnSwitch.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    btnSwitch.classList.toggle("active");

    //Save mode on local storage
    if(document.body.classList.contains("dark")) {
        localStorage.setItem("dark-mode", "true");
    } else {
        localStorage.setItem("dark-mode", "false");
    }
});

if(localStorage.getItem("dark-mode") === "true"){
    document.body.classList.add("dark");
    btnSwitch.classList.add("active");
} else {
    document.body.classList.remove("dark");
    btnSwitch.classList.remove("active");
}