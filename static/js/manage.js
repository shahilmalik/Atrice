document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".filter-checkbox");
  const latecomersTableBody = document.getElementById("latecomersTableBody");

  function updateTable() {
    const selectedFilters = Array.from(checkboxes)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value);

    latecomersTableBody.innerHTML = "";

    // Get the students JSON data from the template
    const studentsJson = "{{ students_json|escapejs }}";
    const students = JSON.parse(studentsJson);

    students.forEach((student, index) => {
      const studentData = {
        sno: index + 1,
        rollNo: student.register_number,
        name: student.name,
        year: student.year,
        specialization: student.specialization,
        section: student.section,
        imageUrl: student.image_url,
      };

      if (
        selectedFilters.includes(studentData.year) &&
        selectedFilters.includes(studentData.specialization) &&
        selectedFilters.includes(studentData.section)
      ) {
        latecomersTableBody.innerHTML += `
            <tr>
              <td>${studentData.sno}</td>
              <td>${studentData.rollNo}</td>
              <td>${studentData.name}</td>
              <td>${studentData.year}</td>
              <td>${studentData.specialization}</td>
              <td>${studentData.section}</td>
              <td>
                <a href="${studentData.imageUrl}" target='_blank'>
                  <button class="view-button">View</button>
                </a>
                <button class="delete-button" data-student-id="${studentData.rollNo}" onclick="confirmDelete(event)">Delete</button>
              </td>
            </tr>
          `;
      }
    });
  }

  // Add event listener to checkboxes
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateTable);
  });

  // Function to handle delete confirmation
  function confirmDelete(event) {
    const deleteButton = event.target;
    const studentId = deleteButton.getAttribute("data-student-id");
    const confirmed = confirm("Are you sure you want to delete this student?");
    if (confirmed) {
      // Make an AJAX request to delete the student record and image
      fetch(`/delete-student/${studentId}/`, {
        method: "DELETE",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Refresh the table
            updateTable();
          }
        })
        .catch((error) => {
          console.error("Error deleting student:", error);
        });
    }
  }

  updateTable();
});
