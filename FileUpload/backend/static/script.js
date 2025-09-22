document.getElementById("deployForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const responseDiv = document.getElementById("response");
  responseDiv.innerText = "Deploying...";
  responseDiv.className = ""; 

  try {
    const response = await fetch("/deploy-sql", {
      method: "POST",
      body: formData
    });

    const result = await response.json();

    responseDiv.innerText = result.message;

    if (result.status === "success") {
      responseDiv.className = "success";
    } else {
      responseDiv.className = "error";
    }
  } catch (err) {
    responseDiv.innerText = "⚠️ Deployment failed. Please try again.";
    responseDiv.className = "error";
  }
});
