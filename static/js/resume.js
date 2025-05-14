document.addEventListener('DOMContentLoaded', function() {
  // DOM Elements
  const resumeForm = document.getElementById('resumeForm');
  const clearFormBtn = document.getElementById('clearForm');
  const previewBtn = document.getElementById('previewBtn');
  const downloadResumeBtn = document.getElementById('downloadResumeBtn');
  const previewSection = document.getElementById('previewSection');
  
  // Section containers
  const educationContainer = document.getElementById('educationContainer');
  const experienceContainer = document.getElementById('experienceContainer');
  const certificationContainer = document.getElementById('certificationContainer');
  
  // Add buttons
  const addEducationBtn = document.getElementById('addEducation');
  const addExperienceBtn = document.getElementById('addExperience');
  const addCertificationBtn = document.getElementById('addCertification');

  // Initialize local storage if available
  initializeFormFromStorage();

  // Event listeners for adding new sections
  addEducationBtn.addEventListener('click', addEducationEntry);
  addExperienceBtn.addEventListener('click', addExperienceEntry);
  addCertificationBtn.addEventListener('click', addCertificationEntry);
  
  // Event listeners for removing entries (using event delegation)
  educationContainer.addEventListener('click', handleRemoveButton);
  experienceContainer.addEventListener('click', handleRemoveButton);
  certificationContainer.addEventListener('click', handleRemoveButton);
  
  // Save form data on submit
  resumeForm.addEventListener('submit', function(e) {
      e.preventDefault();
      saveFormData();
      updatePreview();
      alert('Resume saved successfully!');
  });
  
  // Clear form data
  clearFormBtn.addEventListener('click', function() {
      if (confirm('Are you sure you want to clear all form data? This cannot be undone.')) {
          localStorage.removeItem('resumeData');
          resumeForm.reset();
          resetSections();
          updatePreview();
      }
  });
  
  // Toggle preview on mobile
  previewBtn.addEventListener('click', function() {
      if (window.innerWidth <= 992) {
          previewSection.classList.toggle('visible');
          updatePreview();
      }
  });
  
  // Download PDF
  downloadResumeBtn.addEventListener('click', generatePDF);
  
  // Real-time preview updates
  const formInputs = resumeForm.querySelectorAll('input, textarea');
  formInputs.forEach(input => {
      input.addEventListener('input', updatePreview);
  });
  
  // Initialize preview on page load
  updatePreview();
  
  // Functions
  function addEducationEntry() {
      const newEntry = document.createElement('div');
      newEntry.className = 'education-entry';
      newEntry.innerHTML = `
          <div class="form-group">
              <label>Institution</label>
              <input type="text" name="edu-institution[]" class="form-control" placeholder="e.g. University of California">
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label>Degree</label>
                  <input type="text" name="edu-degree[]" class="form-control" placeholder="e.g. Bachelor of Science">
              </div>
              <div class="form-group">
                  <label>Field of Study</label>
                  <input type="text" name="edu-field[]" class="form-control" placeholder="e.g. Computer Science">
              </div>
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label>Location</label>
                  <input type="text" name="edu-location[]" class="form-control" placeholder="e.g. Berkeley, CA">
              </div>
              <div class="form-group">
                  <label>Date Range</label>
                  <input type="text" name="edu-dates[]" class="form-control" placeholder="e.g. Aug 2018 - May 2022">
              </div>
          </div>
          <button type="button" class="btn-remove"><i class="fas fa-trash"></i> Remove</button>
      `;
      educationContainer.appendChild(newEntry);
      updatePreview();
  }
  
  function addExperienceEntry() {
      const newEntry = document.createElement('div');
      newEntry.className = 'experience-entry';
      newEntry.innerHTML = `
          <div class="form-row">
              <div class="form-group">
                  <label>Job Title</label>
                  <input type="text" name="exp-title[]" class="form-control" placeholder="e.g. Software Engineer">
              </div>
              <div class="form-group">
                  <label>Company</label>
                  <input type="text" name="exp-company[]" class="form-control" placeholder="e.g. Tech Solutions Inc.">
              </div>
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label>Location</label>
                  <input type="text" name="exp-location[]" class="form-control" placeholder="e.g. San Francisco, CA">
              </div>
              <div class="form-group">
                  <label>Date Range</label>
                  <input type="text" name="exp-dates[]" class="form-control" placeholder="e.g. June 2020 - Present">
              </div>
          </div>
          <div class="form-group">
              <label>Responsibilities & Achievements</label>
              <textarea name="exp-description[]" class="form-control" rows="3" placeholder="Describe your key responsibilities and achievements"></textarea>
          </div>
          <button type="button" class="btn-remove"><i class="fas fa-trash"></i> Remove</button>
      `;
      experienceContainer.appendChild(newEntry);
      updatePreview();
  }
  
  function addCertificationEntry() {
      const newEntry = document.createElement('div');
      newEntry.className = 'certification-entry';
      newEntry.innerHTML = `
          <div class="form-group">
              <label>Certification Name</label>
              <input type="text" name="cert-name[]" class="form-control" placeholder="e.g. AWS Certified Solutions Architect">
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label>Issuing Organization</label>
                  <input type="text" name="cert-org[]" class="form-control" placeholder="e.g. Amazon Web Services">
              </div>
              <div class="form-group">
                  <label>Date</label>
                  <input type="text" name="cert-date[]" class="form-control" placeholder="e.g. May 2021">
              </div>
          </div>
          <button type="button" class="btn-remove"><i class="fas fa-trash"></i> Remove</button>
      `;
      certificationContainer.appendChild(newEntry);
      updatePreview();
  }
  
  function handleRemoveButton(e) {
      if (e.target.classList.contains('btn-remove') || e.target.parentElement.classList.contains('btn-remove')) {
          const button = e.target.classList.contains('btn-remove') ? e.target : e.target.parentElement;
          const entry = button.closest('.education-entry, .experience-entry, .certification-entry');
          
          if (entry) {
              entry.remove();
              updatePreview();
          }
      }
  }
  
  function resetSections() {
      // Keep one empty entry in each section
      educationContainer.innerHTML = '';
      experienceContainer.innerHTML = '';
      certificationContainer.innerHTML = '';
      
      addEducationEntry();
      addExperienceEntry();
      addCertificationEntry();
  }
  
  function saveFormData() {
      const formData = new FormData(resumeForm);
      const data = {};
      
      for (const [key, value] of formData.entries()) {
          // Handle array inputs (education, experience, certifications)
          if (key.endsWith('[]')) {
              const baseKey = key.slice(0, -2);
              if (!data[baseKey]) {
                  data[baseKey] = [];
              }
              data[baseKey].push(value);
          } else {
              data[key] = value;
          }
      }
      
      // Structure the data for easier retrieval
      const structuredData = {
          personal: {
              fullName: data.fullName || '',
              email: data.email || '',
              phone: data.phone || '',
              location: data.location || '',
              website: data.website || '',
              summary: data.summary || ''
          },
          education: [],
          experience: [],
          skills: data.skills || '',
          certifications: []
      };
      
      // Process education entries
      const eduCount = data['edu-institution'] ? data['edu-institution'].length : 0;
      for (let i = 0; i < eduCount; i++) {
          structuredData.education.push({
              institution: data['edu-institution'][i] || '',
              degree: data['edu-degree'][i] || '',
              field: data['edu-field'][i] || '',
              location: data['edu-location'][i] || '',
              dates: data['edu-dates'][i] || ''
          });
      }
      
      // Process experience entries
      const expCount = data['exp-title'] ? data['exp-title'].length : 0;
      for (let i = 0; i < expCount; i++) {
          structuredData.experience.push({
              title: data['exp-title'][i] || '',
              company: data['exp-company'][i] || '',
              location: data['exp-location'][i] || '',
              dates: data['exp-dates'][i] || '',
              description: data['exp-description'][i] || ''
          });
      }
      
      // Process certification entries
      const certCount = data['cert-name'] ? data['cert-name'].length : 0;
      for (let i = 0; i < certCount; i++) {
          structuredData.certifications.push({
              name: data['cert-name'][i] || '',
              organization: data['cert-org'][i] || '',
              date: data['cert-date'][i] || ''
          });
      }
      
      // Save to local storage
      localStorage.setItem('resumeData', JSON.stringify(structuredData));
      return structuredData;
  }
  
  function updatePreview() {
      // Get current form data
      const formData = new FormData(resumeForm);
      const data = {};
      
      for (const [key, value] of formData.entries()) {
          if (key.endsWith('[]')) {
              const baseKey = key.slice(0, -2);
              if (!data[baseKey]) {
                  data[baseKey] = [];
              }
              data[baseKey].push(value);
          } else {
              data[key] = value;
          }
      }
      
      // Update personal information
      document.getElementById('previewName').textContent = data.fullName || 'Your Name';
      document.getElementById('previewEmail').textContent = data.email || 'email@example.com';
      document.getElementById('previewPhone').textContent = data.phone || '123-456-7890';
      document.getElementById('previewLocation').textContent = data.location || 'City, State';
      
      const websiteContainer = document.getElementById('previewWebsiteContainer');
      if (data.website) {
          websiteContainer.style.display = 'block';
          document.getElementById('previewWebsite').textContent = data.website;
      } else {
          websiteContainer.style.display = 'none';
      }
      
      document.getElementById('previewSummary').textContent = data.summary || 'Professional summary will appear here...';
      
      // Update education section
      const previewEducation = document.getElementById('previewEducation');
      previewEducation.innerHTML = '';
      
      const eduCount = data['edu-institution'] ? data['edu-institution'].length : 0;
      if (eduCount > 0) {
          for (let i = 0; i < eduCount; i++) {
              if (!data['edu-institution'][i]) continue; // Skip empty entries
              
              const eduItem = document.createElement('div');
              eduItem.className = 'education-item';
              eduItem.innerHTML = `
                  <div class="item-header">
                      <span class="item-title">${data['edu-institution'][i]}</span>
                      <span class="item-date">${data['edu-dates'][i] || 'Date Range'}</span>
                  </div>
                  <div class="item-subheader">
                      <span class="item-subtitle">${data['edu-degree'][i] || ''} ${data['edu-field'][i] ? 'in ' + data['edu-field'][i] : ''}</span>
                      <span class="item-location">${data['edu-location'][i] || ''}</span>
                  </div>
              `;
              previewEducation.appendChild(eduItem);
          }
      } else {
          previewEducation.innerHTML = '<p class="empty-section">No education details added yet.</p>';
      }
      
      // Update experience section
      const previewExperience = document.getElementById('previewExperience');
      previewExperience.innerHTML = '';
      
      const expCount = data['exp-title'] ? data['exp-title'].length : 0;
      if (expCount > 0) {
          for (let i = 0; i < expCount; i++) {
              if (!data['exp-title'][i] && !data['exp-company'][i]) continue; // Skip empty entries
              
              const expItem = document.createElement('div');
              expItem.className = 'experience-item';
              expItem.innerHTML = `
                  <div class="item-header">
                      <span class="item-title">${data['exp-title'][i] || ''} ${data['exp-company'][i] ? 'at ' + data['exp-company'][i] : ''}</span>
                      <span class="item-date">${data['exp-dates'][i] || 'Date Range'}</span>
                  </div>
                  <div class="item-subheader">
                      <span class="item-location">${data['exp-location'][i] || ''}</span>
                  </div>
                  <div class="item-description">
                      <p>${data['exp-description'][i] || 'Job description will appear here...'}</p>
                  </div>
              `;
              previewExperience.appendChild(expItem);
          }
      } else {
          previewExperience.innerHTML = '<p class="empty-section">No experience details added yet.</p>';
      }
      
      // Update skills section
      const previewSkills = document.getElementById('previewSkills');
      previewSkills.innerHTML = '';
      
      if (data.skills) {
          const skillsList = data.skills.split(',').map(skill => skill.trim()).filter(skill => skill);
          skillsList.forEach(skill => {
              const skillTag = document.createElement('span');
              skillTag.className = 'skill-tag';
              skillTag.textContent = skill;
              previewSkills.appendChild(skillTag);
          });
      } else {
          previewSkills.innerHTML = '<p class="empty-section">No skills added yet.</p>';
      }
      
      // Update certifications section
      const previewCertifications = document.getElementById('previewCertifications');
      previewCertifications.innerHTML = '';
      
      const certCount = data['cert-name'] ? data['cert-name'].length : 0;
      if (certCount > 0) {
          for (let i = 0; i < certCount; i++) {
              if (!data['cert-name'][i]) continue; // Skip empty entries
              
              const certItem = document.createElement('div');
              certItem.className = 'certification-item';
              certItem.innerHTML = `
                  <div class="item-header">
                      <span class="item-title">${data['cert-name'][i]}</span>
                      <span class="item-date">${data['cert-date'][i] || 'Date'}</span>
                  </div>
                  <div class="item-subheader">
                      <span class="item-subtitle">${data['cert-org'][i] || ''}</span>
                  </div>
              `;
              previewCertifications.appendChild(certItem);
          }
      } else {
          previewCertifications.innerHTML = '<p class="empty-section">No certifications added yet.</p>';
      }
      
      // Show/hide certifications section if empty
      document.getElementById('certificationsSection').style.display = certCount > 0 ? 'block' : 'none';
  }
  
  function generatePDF() {
      // Configure pdf options
      const options = {
          margin: 10,
          filename: 'resume.pdf',
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      // Get the element to convert
      const element = document.querySelector('.preview-container');
      
      // Generate PDF
      html2pdf().from(element).set(options).save();
  }
  
  function initializeFormFromStorage() {
      const savedData = localStorage.getItem('resumeData');
      if (!savedData) return;
      
      try {
          const data = JSON.parse(savedData);
          
          // Fill in personal details
          document.getElementById('fullName').value = data.personal.fullName || '';
          document.getElementById('email').value = data.personal.email || '';
          document.getElementById('phone').value = data.personal.phone || '';
          document.getElementById('location').value = data.personal.location || '';
          document.getElementById('website').value = data.personal.website || '';
          document.getElementById('summary').value = data.personal.summary || '';
          document.getElementById('skills').value = data.skills || '';
          
          // Clear existing sections
          educationContainer.innerHTML = '';
          experienceContainer.innerHTML = '';
          certificationContainer.innerHTML = '';
          
          // Add education entries
          if (data.education && data.education.length) {
              data.education.forEach(edu => {
                  const entry = document.createElement('div');
                  entry.className = 'education-entry';
                  entry.innerHTML = `
                      <div class="form-group">
                          <label>Institution</label>
                          <input type="text" name="edu-institution[]" class="form-control" value="${edu.institution}" placeholder="e.g. University of California">
                      </div>
                      <div class="form-row">
                          <div class="form-group">
                              <label>Degree</label>
                              <input type="text" name="edu-degree[]" class="form-control" value="${edu.degree}" placeholder="e.g. Bachelor of Science">
                          </div>
                          <div class="form-group">
                              <label>Field of Study</label>
                              <input type="text" name="edu-field[]" class="form-control" value="${edu.field}" placeholder="e.g. Computer Science">
                          </div>
                      </div>
                      <div class="form-row">
                          <div class="form-group">
                              <label>Location</label>
                              <input type="text" name="edu-location[]" class="form-control" value="${edu.location}" placeholder="e.g. Berkeley, CA">
                          </div>
                          <div class="form-group">
                              <label>Date Range</label>
                              <input type="text" name="edu-dates[]" class="form-control" value="${edu.dates}" placeholder="e.g. Aug 2018 - May 2022">
                          </div>
                      </div>
                      <button type="button" class="btn-remove"><i class="fas fa-trash"></i> Remove</button>
                  `;
                  educationContainer.appendChild(entry);
              });
          } else {
              addEducationEntry(); // Add an empty one if none exists
          }
          
          // Add experience entries
          if (data.experience && data.experience.length) {
              data.experience.forEach(exp => {
                  const entry = document.createElement('div');
                  entry.className = 'experience-entry';
                  entry.innerHTML = `
                      <div class="form-row">
                          <div class="form-group">
                              <label>Job Title</label>
                              <input type="text" name="exp-title[]" class="form-control" value="${exp.title}" placeholder="e.g. Software Engineer">
                          </div>
                          <div class="form-group">
                              <label>Company</label>
                              <input type="text" name="exp-company[]" class="form-control" value="${exp.company}" placeholder="e.g. Tech Solutions Inc.">
                          </div>
                      </div>
                      <div class="form-row">
                          <div class="form-group">
                              <label>Location</label>
                              <input type="text" name="exp-location[]" class="form-control" value="${exp.location}" placeholder="e.g. San Francisco, CA">
                          </div>
                          <div class="form-group">
                              <label>Date Range</label>
                              <input type="text" name="exp-dates[]" class="form-control" value="${exp.dates}" placeholder="e.g. June 2020 - Present">
                          </div>
                      </div>
                      <div class="form-group">
                          <label>Responsibilities & Achievements</label>
                          <textarea name="exp-description[]" class="form-control" rows="3" placeholder="Describe your key responsibilities and achievements">${exp.description}</textarea>
                      </div>
                      <button type="button" class="btn-remove"><i class="fas fa-trash"></i> Remove</button>
                  `;
                  experienceContainer.appendChild(entry);
              });
          } else {
              addExperienceEntry(); // Add an empty one if none exists
          }
          
          // Add certification entries
          if (data.certifications && data.certifications.length) {
              data.certifications.forEach(cert => {
                  const entry = document.createElement('div');
                  entry.className = 'certification-entry';
                  entry.innerHTML = `
                      <div class="form-group">
                          <label>Certification Name</label>
                          <input type="text" name="cert-name[]" class="form-control" value="${cert.name}" placeholder="e.g. AWS Certified Solutions Architect">
                      </div>
                      <div class="form-row">
                          <div class="form-group">
                              <label>Issuing Organization</label>
                              <input type="text" name="cert-org[]" class="form-control" value="${cert.organization}" placeholder="e.g. Amazon Web Services">
                          </div>
                          <div class="form-group">
                              <label>Date</label>
                              <input type="text" name="cert-date[]" class="form-control" value="${cert.date}" placeholder="e.g. May 2021">
                          </div>
                      </div>
                      <button type="button" class="btn-remove"><i class="fas fa-trash"></i> Remove</button>
                  `;
                  certificationContainer.appendChild(entry);
              });
          } else {
              addCertificationEntry(); // Add an empty one if none exists
          }
          
      } catch (e) {
          console.error('Error loading saved data:', e);
          resetSections();
      }
  }
});