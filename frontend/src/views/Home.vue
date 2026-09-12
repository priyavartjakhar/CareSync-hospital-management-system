<template>
  <div id="caresync-home">
    <!-- ══════════════ NAVBAR ══════════════ -->
    <nav class="navbar">
      <div class="nav-inner">
        <div class="logo">Care<span>Sync</span></div>

        <div class="nav-group">
          <div class="nav-links">
            <a href="#how">How it works</a>
            <a href="#specializations">Specializations</a>
            <a href="#doctors">Doctors</a>
            <a href="#contact">Contact</a>
          </div>

          <div class="nav-right">
            <div class="login-wrap">
              <button class="login-btn">
                <svg
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Log in
                <svg
                  class="chevron"
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>
              <div class="dropdown">
                <router-link to="/patient/login" class="dropdown-item">
                  <div class="d-icon" style="background: #e1f5ee">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#0F6E56"
                      stroke-width="1.8"
                    >
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </div>
                  <div>
                    <div class="di-title">Patient login</div>
                    <div class="di-sub">Book &amp; manage appointments</div>
                  </div>
                </router-link>
                <router-link to="/doctor/login" class="dropdown-item">
                  <div class="d-icon" style="background: #e6f1fb">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#185FA5"
                      stroke-width="1.8"
                    >
                      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                    </svg>
                  </div>
                  <div>
                    <div class="di-title">Doctor login</div>
                    <div class="di-sub">View patients &amp; appointments</div>
                  </div>
                </router-link>
                <hr class="dropdown-divider" />
                <router-link to="/admin/login" class="dropdown-item">
                  <div class="d-icon" style="background: #eeedfe">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#534AB7"
                      stroke-width="1.8"
                    >
                      <rect x="3" y="3" width="7" height="7" />
                      <rect x="14" y="3" width="7" height="7" />
                      <rect x="3" y="14" width="7" height="7" />
                      <rect x="14" y="14" width="7" height="7" />
                    </svg>
                  </div>
                  <div>
                    <div class="di-title">Admin login</div>
                    <div class="di-sub">Manage doctors &amp; staff</div>
                  </div>
                </router-link>
                <hr class="dropdown-divider" />
                <router-link to="/patient/register" class="dropdown-item">
                  <div class="d-icon" style="background: #f1efe8">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#5F5E5A"
                      stroke-width="1.8"
                    >
                      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <line x1="19" y1="8" x2="19" y2="14" />
                      <line x1="22" y1="11" x2="16" y2="11" />
                    </svg>
                  </div>
                  <div>
                    <div class="di-title">Register as patient</div>
                    <div class="di-sub">New to CareSync?</div>
                  </div>
                </router-link>
              </div>
            </div>
            <router-link to="/patient/register" class="btn-primary"
              >Get started</router-link
            >
          </div>
        </div>
      </div>
    </nav>

    <!-- ══════════════ HERO ══════════════ -->
    <section class="hero" id="home">
      <div class="hero-inner">
        <div class="hero-text">
          <h1>Your health,<br /><em>seamlessly</em><br />managed.</h1>

          <p>
            CareSync connects patients, doctors, and hospital staff on one
            intelligent platform — appointments, diagnoses, and care history,
            effortlessly in one place.
          </p>
          <div class="hero-actions">
            <router-link to="/patient/register" class="btn-primary btn-lg"
              >Book appointment</router-link
            >
            <router-link to="/doctor/login" class="btn-ghost btn-lg"
              >I'm a doctor →</router-link
            >
          </div>
          <div class="hero-meta">
            <div class="meta-item">
              <strong>500+</strong>
              <span>Verified doctors</span>
            </div>
            <div class="meta-sep"></div>
            <div class="meta-item">
              <strong>12,000+</strong>
              <span>Patients served</span>
            </div>
            <div class="meta-sep"></div>
            <div class="meta-item">
              <strong>48k+</strong>
              <span>Appointments done</span>
            </div>
          </div>
        </div>

        <div class="hero-visual">
          <!-- Doctor-patient consultation image from Unsplash -->
          <img
            src="/hero_index.png"
            alt="Doctor consulting with patient"
            class="hero-img"
          />
          <!-- Floating cards -->
          <div class="float-card float-confirmed">
            <div class="fc-icon fc-green">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="2.2"
              >
                <path d="M20 6L9 17l-5-5" />
              </svg>
            </div>
            <div>
              <div class="fc-title">Appointment Confirmed</div>
              <div class="fc-sub">Today · 10:30 AM · Dr. Priya Sharma</div>
            </div>
          </div>
          <div class="float-card float-reminder">
            <div class="fc-icon fc-amber">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#BA7517"
                stroke-width="2"
              >
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
            </div>
            <div>
              <div class="fc-title">Daily Reminders Sent</div>
              <div class="fc-sub">12 patients notified · 8:00 AM</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════ STATS BAR ══════════════ -->
    <section class="stats-bar">
      <div class="stats-inner">
        <div class="stat-item">
          <div class="stat-n">500+</div>
          <div class="stat-l">Registered doctors</div>
        </div>
        <div class="stat-item">
          <div class="stat-n">12k+</div>
          <div class="stat-l">Patients served</div>
        </div>
        <div class="stat-item">
          <div class="stat-n">20</div>
          <div class="stat-l">Specializations</div>
        </div>
        <div class="stat-item">
          <div class="stat-n">48k+</div>
          <div class="stat-l">Appointments done</div>
        </div>
        <div class="stat-item">
          <div class="stat-n">4.9★</div>
          <div class="stat-l">Average rating</div>
        </div>
      </div>
    </section>

    <!-- ══════════════ HOW IT WORKS ══════════════ -->
    <section class="section" id="how">
      <div class="wide-container">
        <div class="section-header">
          <div>
            <div class="section-tag">How it works</div>
            <h2 class="section-title">Healthcare in three steps</h2>
          </div>
          <p class="section-sub">
            From registration to recovery — simple, transparent, and built
            around you.
          </p>
        </div>
        <div class="steps">
          <div class="step">
            <div class="step-num">01</div>
            <div class="step-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <h3>Create your profile</h3>
            <p>
              Sign up in under two minutes. Add health information, allergies,
              and medical history for personalised care.
            </p>
          </div>
          <div class="step-arrow">→</div>
          <div class="step">
            <div class="step-num">02</div>
            <div class="step-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
            </div>
            <h3>Find your doctor</h3>
            <p>
              Browse specialists by department or availability. Check profiles
              and book the right doctor instantly.
            </p>
          </div>
          <div class="step-arrow">→</div>
          <div class="step">
            <div class="step-num">03</div>
            <div class="step-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
            </div>
            <h3>Book and track</h3>
            <p>
              Confirm appointments, receive smart reminders, and view your
              complete treatment history from one dashboard.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════ SPECIALIZATIONS ══════════════ -->
    <section class="section section-alt" id="specializations">
      <div class="wide-container">
        <div class="section-header">
          <div>
            <div class="section-tag">Departments</div>
            <h2 class="section-title">
              Expert care across all specializations
            </h2>
          </div>
          <p class="section-sub">
            Our network covers a comprehensive range of medical disciplines — so
            you always find the right expert.
          </p>
        </div>
        <div class="spec-grid">
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <path
                  d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                />
              </svg>
            </div>
            <h4>Cardiology</h4>
            <p>Heart &amp; cardiovascular care</p>
            <span class="spec-count">42 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <path
                  d="M12 2a9 9 0 0 1 9 9c0 3.18-1.65 5.97-4.13 7.6L16 22H8l.13-3.4A9 9 0 0 1 3 11a9 9 0 0 1 9-9z"
                />
              </svg>
            </div>
            <h4>Neurology</h4>
            <p>Brain &amp; nervous system</p>
            <span class="spec-count">28 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <line x1="12" y1="3" x2="12" y2="21" />
                <path d="M8 7l4-4 4 4" />
                <path d="M8 17l4 4 4-4" />
              </svg>
            </div>
            <h4>Orthopedics</h4>
            <p>Bones, joints &amp; muscles</p>
            <span class="spec-count">35 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <circle cx="12" cy="12" r="2" />
                <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z" />
              </svg>
            </div>
            <h4>Ophthalmology</h4>
            <p>Eye care &amp; vision health</p>
            <span class="spec-count">19 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <circle cx="9" cy="7" r="4" />
                <path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                <path d="M21 21v-2a4 4 0 0 0-3-3.85" />
              </svg>
            </div>
            <h4>Pediatrics</h4>
            <p>Child health &amp; development</p>
            <span class="spec-count">38 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </div>
            <h4>Oncology</h4>
            <p>Cancer diagnosis &amp; therapy</p>
            <span class="spec-count">24 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h4>Gynecology</h4>
            <p>Women &amp; pregnancy care</p>
            <span class="spec-count">33 doctors</span>
          </div>
          <div class="spec-card">
            <div class="spec-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <path d="M4 12c0-4.4 3.6-8 8-8s8 3.6 8 8" />
                <path d="M8 12c0-2.2 1.8-4 4-4s4 1.8 4 4" />
                <circle cx="12" cy="12" r="2" />
                <path d="M12 14v4" />
                <path d="M10 18h4" />
              </svg>
            </div>
            <h4>Pulmonology</h4>
            <p>Lung &amp; respiratory care</p>
            <span class="spec-count">22 doctors</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════ FEATURES ══════════════ -->
    <section class="section" id="features">
      <div class="wide-container">
        <div class="section-header">
          <div>
            <div class="section-tag">Platform features</div>
            <h2 class="section-title">
              Everything you need, nothing you don't
            </h2>
          </div>
          <p class="section-sub">
            Built for every stakeholder — from first-time patients to doctors
            managing hundreds of cases daily.
          </p>
        </div>
        <div class="features-grid">
          <div class="feat-card">
            <div class="feat-icon" style="background: #e1f5ee">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0F6E56"
                stroke-width="1.8"
              >
                <rect x="3" y="11" width="18" height="11" rx="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <h4>Role-based access</h4>
            <p>
              Separate secure dashboards for admins, doctors, and patients —
              everyone sees exactly what they need.
            </p>
          </div>
          <div class="feat-card">
            <div class="feat-icon" style="background: #e6f1fb">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#185FA5"
                stroke-width="1.8"
              >
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <line x1="3" y1="10" x2="21" y2="10" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="16" y1="2" x2="16" y2="6" />
              </svg>
            </div>
            <h4>Smart scheduling</h4>
            <p>
              Conflict-free bookings with real-time doctor availability. No
              double-bookings, no errors.
            </p>
          </div>
          <div class="feat-card">
            <div class="feat-icon" style="background: #eeedfe">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#534AB7"
                stroke-width="1.8"
              >
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            </div>
            <h4>Full treatment history</h4>
            <p>
              Every diagnosis, prescription, and note stored securely. Doctors
              get the complete picture every time.
            </p>
          </div>
          <div class="feat-card">
            <div class="feat-icon" style="background: #faeeda">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#854F0B"
                stroke-width="1.8"
              >
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
            </div>
            <h4>Automated reminders</h4>
            <p>
              Daily reminders via email or chat so patients never miss an
              appointment or follow-up.
            </p>
          </div>
          <div class="feat-card">
            <div class="feat-icon" style="background: #eaf3de">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#3B6D11"
                stroke-width="1.8"
              >
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
            </div>
            <h4>Monthly reports</h4>
            <p>
              Auto-generated activity reports for doctors — all appointments,
              diagnoses, and treatments included.
            </p>
          </div>
          <div class="feat-card">
            <div class="feat-icon" style="background: #fbeaf0">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#993556"
                stroke-width="1.8"
              >
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                />
                <polyline points="14 2 14 8 20 8" />
                <line x1="8" y1="13" x2="16" y2="13" />
                <line x1="8" y1="17" x2="13" y2="17" />
              </svg>
            </div>
            <h4>CSV export</h4>
            <p>
              Patients can export their full treatment history as CSV — useful
              for insurance and second opinions.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════ DOCTORS ══════════════ -->
    <section class="section section-alt" id="doctors">
      <div class="wide-container">
        <div class="section-header">
          <div>
            <div class="section-tag">Our specialists</div>
            <h2 class="section-title">Meet our top doctors</h2>
          </div>
          <p class="section-sub">
            Verified professionals with years of experience and a genuine
            commitment to patient care.
          </p>
        </div>
        <div class="docs-grid">
          <div class="doc-card">
            <div class="doc-head doc-head--teal">
              <div class="doc-av doc-av--teal">PS</div>
              <div>
                <div class="doc-name doc-name--teal">Dr. Priya Sharma</div>
                <div class="doc-spec doc-spec--teal">Cardiologist</div>
              </div>
            </div>
            <div class="doc-body">
              <div class="doc-row">
                <span>Experience</span><strong>12 years</strong>
              </div>
              <div class="doc-row">
                <span>Patients</span><strong>840</strong>
              </div>
              <div class="doc-rating">
                <span class="stars">★★★★★</span
                ><span class="rating-val">5.0</span
                ><span class="rating-cnt">(128 reviews)</span>
              </div>
              <router-link to="/patient/login" class="doc-btn"
                >Book appointment</router-link
              >
            </div>
          </div>
          <div class="doc-card">
            <div class="doc-head doc-head--blue">
              <div class="doc-av doc-av--blue">AM</div>
              <div>
                <div class="doc-name doc-name--blue">Dr. Arjun Mehta</div>
                <div class="doc-spec doc-spec--blue">Neurologist</div>
              </div>
            </div>
            <div class="doc-body">
              <div class="doc-row">
                <span>Experience</span><strong>9 years</strong>
              </div>
              <div class="doc-row">
                <span>Patients</span><strong>620</strong>
              </div>
              <div class="doc-rating">
                <span class="stars">★★★★★</span
                ><span class="rating-val">4.9</span
                ><span class="rating-cnt">(96 reviews)</span>
              </div>
              <router-link to="/patient/login" class="doc-btn doc-btn--blue"
                >Book appointment</router-link
              >
            </div>
          </div>
          <div class="doc-card">
            <div class="doc-head doc-head--purple">
              <div class="doc-av doc-av--purple">RN</div>
              <div>
                <div class="doc-name doc-name--purple">Dr. Rekha Nair</div>
                <div class="doc-spec doc-spec--purple">Orthopedic surgeon</div>
              </div>
            </div>
            <div class="doc-body">
              <div class="doc-row">
                <span>Experience</span><strong>15 years</strong>
              </div>
              <div class="doc-row">
                <span>Patients</span><strong>1,100</strong>
              </div>
              <div class="doc-rating">
                <span class="stars">★★★★★</span
                ><span class="rating-val">4.8</span
                ><span class="rating-cnt">(204 reviews)</span>
              </div>
              <router-link to="/patient/login" class="doc-btn doc-btn--purple"
                >Book appointment</router-link
              >
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════ TESTIMONIALS ══════════════ -->
    <section class="section" id="testimonials">
      <div class="wide-container">
        <div class="section-header">
          <div>
            <div class="section-tag">Patient stories</div>
            <h2 class="section-title">Trusted by thousands</h2>
          </div>
          <p class="section-sub">
            Real experiences from patients and doctors who rely on CareSync
            every day.
          </p>
        </div>
        <div class="testi-grid">
          <div class="testi-card">
            <div class="testi-stars-top">★★★★★</div>
            <p class="testi-quote">
              "Booking used to be a nightmare. With CareSync I found a
              cardiologist, checked availability, and confirmed in under five
              minutes. The reminder feature is a lifesaver."
            </p>
            <div class="testi-author">
              <div class="testi-av" style="background: #e1f5ee; color: #085041">
                AK
              </div>
              <div>
                <div class="testi-name">Ananya Kapoor</div>
                <div class="testi-role">Patient, Delhi</div>
              </div>
            </div>
          </div>
          <div class="testi-card">
            <div class="testi-stars-top">★★★★★</div>
            <p class="testi-quote">
              "Managing 30+ patients daily, the dashboard is incredibly
              thoughtful. I see my full schedule, update treatment notes, and my
              monthly report just appears in my inbox."
            </p>
            <div class="testi-author">
              <div class="testi-av" style="background: #e6f1fb; color: #0c447c">
                SR
              </div>
              <div>
                <div class="testi-name">Dr. Sameer Rathi</div>
                <div class="testi-role">Physician, Mumbai</div>
              </div>
            </div>
          </div>
          <div class="testi-card">
            <div class="testi-stars-top">★★★★★</div>
            <p class="testi-quote">
              "Managing records for 200 doctors used to need three different
              systems. CareSync consolidated everything. The admin panel is
              clean, fast, and has everything we need."
            </p>
            <div class="testi-author">
              <div class="testi-av" style="background: #faeeda; color: #633806">
                MP
              </div>
              <div>
                <div class="testi-name">Meera Pillai</div>
                <div class="testi-role">Hospital admin, Bangalore</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════ CTA ══════════════ -->
    <section class="cta-band" id="contact">
      <div class="wide-container cta-inner">
        <div class="cta-text">
          <h2>Ready to take control of your health?</h2>
          <p>
            Join thousands of patients and doctors who've made CareSync their
            trusted healthcare companion. Free to register.
          </p>
        </div>
        <div class="cta-btns">
          <router-link
            to="/patient/register"
            class="btn-primary btn-lg cta-btn-primary"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            >
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <line x1="19" y1="8" x2="19" y2="14" />
              <line x1="22" y1="11" x2="16" y2="11" />
            </svg>
            Register as patient
          </router-link>
          <router-link to="/doctor/login" class="btn-ghost-teal btn-lg">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
            Are you a doctor?
          </router-link>
        </div>
      </div>
    </section>

    <!-- ══════════════ FOOTER ══════════════ -->
    <footer>
      <div class="wide-container footer-inner">
        <div class="footer-brand">
          <span
            style="font-size: 20px; font-weight: 800; letter-spacing: -0.4px"
            >Care<span style="color: #0f6e56">Sync</span></span
          >
          <p>
            Your complete hospital management system — connecting patients,
            doctors, and staff seamlessly.
          </p>
        </div>

        <div class="footer-col">
          <h5>Platform</h5>
          <router-link to="/patient/login">Patient portal</router-link>
          <router-link to="/doctor/login">Doctor dashboard</router-link>
          <router-link to="/admin/login">Admin panel</router-link>
          <router-link to="/patient/register">Book appointment</router-link>
        </div>
        <div class="footer-col">
          <h5>Specializations</h5>
          <a href="#">Cardiology</a>
          <a href="#">Neurology</a>
          <a href="#">Orthopedics</a>
          <a href="#">Pediatrics</a>
        </div>
        <div class="footer-col">
          <h5>Company</h5>
          <a href="#">About us</a>
          <a href="#">Careers</a>
          <a href="#">Privacy policy</a>
          <a href="#">Contact</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 CareSync. All rights reserved.</span>
      </div>
    </footer>
  </div>
</template>

<script>
import { onMounted, onBeforeUnmount } from "vue";

export default {
  name: "Home",
  setup() {
    let revealObserver = null;
    const anchorHandlers = [];

    onMounted(() => {
      const reveals = document.querySelectorAll(".reveal");
      revealObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) entry.target.classList.add("visible");
          });
        },
        { threshold: 0.12 },
      );
      reveals.forEach((r) => revealObserver.observe(r));

      document.querySelectorAll('a[href^="#"]').forEach((a) => {
        const handler = (e) => {
          const target = document.querySelector(a.getAttribute("href"));
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        };
        a.addEventListener("click", handler);
        anchorHandlers.push([a, handler]);
      });
    });

    onBeforeUnmount(() => {
      if (revealObserver) revealObserver.disconnect();
      anchorHandlers.forEach(([a, handler]) =>
        a.removeEventListener("click", handler),
      );
    });
  },
};
</script>

<style scoped>
/* ════════════════════════════════
   CSS VARIABLES
════════════════════════════════ */
#caresync-home {
  --teal: #0f6e56;
  --teal-dark: #085041;
  --teal-deeper: #04342c;
  --teal-light: #e1f5ee;
  --teal-mid: #9fe1cb;
  --blue-light: #e6f1fb;
  --blue: #185fa5;
  --purple-light: #eeedfe;
  --purple: #534ab7;
  --charcoal: #0f172a;
  --slate: #1e293b;
  --muted: #64748b;
  --light: #f8fafc;
  --white: #ffffff;
  --border: rgba(0, 0, 0, 0.08);
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-xl: 24px;

  font-family:
    "Segoe UI",
    system-ui,
    -apple-system,
    sans-serif;
  color: var(--charcoal);
  background: var(--white);
  overflow-x: hidden;
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
a {
  text-decoration: none;
  color: inherit;
}
img {
  display: block;
  max-width: 100%;
}

/* ── Full-width container ── */
.wide-container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 48px;
}

/* ════════════════════════════════
   BUTTONS
════════════════════════════════ */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: var(--teal);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  padding: 9px 20px;
  cursor: pointer;
  transition:
    background 0.2s,
    transform 0.15s;
  font-family: inherit;
}
.btn-primary:hover {
  background: var(--teal-dark);
  transform: translateY(-1px);
  color: #fff;
}
.btn-primary.btn-lg {
  font-size: 15px;
  padding: 12px 26px;
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: transparent;
  color: var(--charcoal);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  padding: 9px 20px;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
  font-family: inherit;
}
.btn-ghost:hover {
  background: var(--light);
  border-color: #ccc;
}
.btn-ghost.btn-lg {
  font-size: 15px;
  padding: 12px 26px;
}

.btn-ghost-teal {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: transparent;
  color: var(--teal-dark);
  border: 1.5px solid var(--teal);
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  padding: 11px 22px;
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
}
.btn-ghost-teal:hover {
  background: rgba(15, 110, 86, 0.08);
}
.btn-ghost-teal.btn-lg {
  font-size: 15px;
}

/* ════════════════════════════════
   NAVBAR — full bleed
════════════════════════════════ */

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.98);

  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 48px;
  display: flex;
  align-items: center;
  height: 75px;
  gap: 300px; /* gap between logo and nav links */
}

.logo {
  font-size: 30px;
  font-weight: 900;
  letter-spacing: -0.5px;
  color: var(--charcoal);
  flex-shrink: 0;
}

.logo span {
  color: var(--teal);
}

.nav-links {
  display: flex;
  gap: 2px;
}
.nav-links a {
  font-size: 14px;
  color: var(--muted);
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  transition:
    background 0.15s,
    color 0.15s;
  font-weight: 500;
}
.nav-links a:hover {
  background: var(--light);
  color: var(--charcoal);
}

.nav-group {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Login Dropdown */
.login-wrap {
  position: relative;
}
.login-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  padding: 8px 16px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--charcoal);
  cursor: pointer;
  transition: background 0.15s;
  font-family: inherit;
  font-weight: 500;
}
.login-btn:hover,
.login-wrap:hover .login-btn {
  background: var(--light);
}
.chevron {
  transition: transform 0.2s;
}
.login-wrap:hover .chevron {
  transform: rotate(180deg);
}
.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  min-width: 224px;
  padding: 8px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-8px);
  transition:
    opacity 0.18s,
    transform 0.18s;
  z-index: 200;
}
.login-wrap:hover .dropdown {
  opacity: 1;
  pointer-events: all;
  transform: translateY(0);
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  transition: background 0.12s;
  color: var(--charcoal);
}
.dropdown-item:hover {
  background: var(--light);
}
.d-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.d-icon svg {
  width: 16px;
  height: 16px;
}
.di-title {
  font-size: 13px;
  font-weight: 600;
}
.di-sub {
  font-size: 11px;
  color: var(--muted);
  margin-top: 1px;
}
.dropdown-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 6px 0;
}

/* ════════════════════════════════
   HERO — full bleed with side padding
════════════════════════════════ */
.hero {
  background: linear-gradient(160deg, #f0fdf8 0%, #ffffff 60%);
  padding: 0;
  overflow: hidden;
}

.hero-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 160px 48px 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: start;
  min-height: calc(100vh - 128px);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--teal-light);
  color: var(--teal-dark);
  border: 1px solid var(--teal-mid);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  padding: 6px 14px;
  margin-bottom: 24px;
}
.badge-dot {
  width: 7px;
  height: 7px;
  background: var(--teal);
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.4);
  }
}

.hero-text h1 {
  font-size: clamp(40px, 5vw, 58px);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -1.5px;
  margin-bottom: 20px;
  color: var(--charcoal);
}
.hero-text h1 em {
  font-style: normal;
  color: var(--teal);
}

.hero-text > p {
  font-size: 17px;
  color: var(--muted);
  line-height: 1.75;
  margin-bottom: 44px;
  max-width: 440px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 36px;
}
.hero-meta {
  display: flex;
  align-items: center;
  gap: 0;
}
.meta-item {
  text-align: left;
  padding: 0 24px;
}
.meta-item:first-child {
  padding-left: 0;
}
.meta-item strong {
  font-size: 20px;
  font-weight: 800;
  color: var(--charcoal);
  display: block;
  line-height: 1;
}
.meta-item span {
  font-size: 12px;
  color: var(--muted);
  margin-top: 3px;
  display: block;
}
.meta-sep {
  width: 1px;
  height: 32px;
  background: var(--border);
}

/* Hero image area */

.hero-visual {
  position: relative;
  align-self: flex-start;
  padding-bottom: 0;
}

.hero-img {
  width: 100%;
  height: 480px;
  object-fit: cover;
  object-position: center;
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  display: block;
}

/* Floating cards */
.float-card {
  position: absolute;
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  min-width: 240px;
  animation: floatUp 0.8s ease forwards;
}

.float-confirmed {
  bottom: 120px;
  left: -40px;
  animation-delay: 0.3s;
}
.float-reminder {
  top: 20px;
  right: -24px;
  animation-delay: 0.5s;
}

@keyframes floatUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.fc-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.fc-green {
  background: var(--teal-light);
}
.fc-amber {
  background: #faeeda;
}
.fc-icon svg {
  width: 18px;
  height: 18px;
}
.fc-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--charcoal);
}
.fc-sub {
  font-size: 11px;
  color: var(--muted);
  margin-top: 2px;
}

/* ════════════════════════════════
   STATS BAR — full bleed
════════════════════════════════ */
.stats-bar {
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  background: var(--white);
  padding: 32px 0;
}
.stats-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-item {
  text-align: center;
  flex: 1;
}
.stat-item + .stat-item {
  border-left: 1px solid var(--border);
}
.stat-n {
  font-size: 30px;
  font-weight: 800;
  color: var(--teal);
  line-height: 1;
}
.stat-l {
  font-size: 13px;
  color: var(--muted);
  margin-top: 5px;
}

/* ════════════════════════════════
   SHARED SECTION STYLES
════════════════════════════════ */
.section {
  padding: 80px 0;
}
.section-alt {
  background: var(--light);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 48px;
  gap: 32px;
}
.section-tag {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--teal);
  margin-bottom: 10px;
}
.section-title {
  font-size: clamp(24px, 3vw, 34px);
  font-weight: 800;
  letter-spacing: -0.6px;
  line-height: 1.2;
  color: var(--charcoal);
}
.section-sub {
  font-size: 15px;
  color: var(--muted);
  line-height: 1.7;
  max-width: 380px;
  align-self: flex-end;
  flex-shrink: 0;
}

/* ════════════════════════════════
   HOW IT WORKS
════════════════════════════════ */
.steps {
  display: flex;
  align-items: stretch;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--border);
}
.step {
  flex: 1;
  background: var(--white);
  padding: 36px 32px;
}
.step-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--white);
  font-size: 22px;
  color: var(--teal-mid);
  padding: 0 4px;
  flex-shrink: 0;
}
.step-num {
  font-size: 11px;
  font-weight: 800;
  color: var(--teal);
  letter-spacing: 0.1em;
  margin-bottom: 18px;
  text-transform: uppercase;
}
.step-icon {
  width: 44px;
  height: 44px;
  background: var(--teal-light);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.step-icon svg {
  width: 20px;
  height: 20px;
}
.step h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}
.step p {
  font-size: 14px;
  color: var(--muted);
  line-height: 1.65;
}

/* ════════════════════════════════
   SPECIALIZATIONS
════════════════════════════════ */
.spec-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.spec-card {
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  padding: 24px 20px;
  cursor: pointer;
  transition:
    border-color 0.18s,
    transform 0.2s,
    box-shadow 0.2s;
}
.spec-card:hover {
  border-color: var(--teal);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(15, 110, 86, 0.1);
}
.spec-icon {
  width: 42px;
  height: 42px;
  background: var(--teal-light);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}
.spec-icon svg {
  width: 20px;
  height: 20px;
}
.spec-card h4 {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}
.spec-card p {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.55;
}
.spec-count {
  display: inline-block;
  font-size: 11px;
  color: var(--teal-dark);
  background: var(--teal-light);
  padding: 3px 10px;
  border-radius: 20px;
  margin-top: 10px;
  font-weight: 600;
}

/* ════════════════════════════════
   FEATURES
════════════════════════════════ */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.feat-card {
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  padding: 28px 24px;
  transition:
    border-color 0.18s,
    box-shadow 0.2s;
}
.feat-card:hover {
  border-color: var(--teal-mid);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}
.feat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.feat-icon svg {
  width: 18px;
  height: 18px;
}
.feat-card h4 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 7px;
}
.feat-card p {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.65;
}

/* ════════════════════════════════
   DOCTORS
════════════════════════════════ */
.docs-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.doc-card {
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition:
    border-color 0.2s,
    transform 0.2s,
    box-shadow 0.2s;
  background: var(--white);
}
.doc-card:hover {
  border-color: var(--teal);
  transform: translateY(-5px);
  box-shadow: 0 16px 40px rgba(15, 110, 86, 0.1);
}
.doc-head {
  padding: 24px 22px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.doc-head--teal {
  background: var(--teal-light);
}
.doc-head--blue {
  background: var(--blue-light);
}
.doc-head--purple {
  background: var(--purple-light);
}
.doc-av {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
}
.doc-av--teal {
  background: var(--teal-mid);
  color: var(--teal-dark);
}
.doc-av--blue {
  background: #b5d4f4;
  color: #0c447c;
}
.doc-av--purple {
  background: #cecbf6;
  color: #26215c;
}
.doc-name {
  font-size: 15px;
  font-weight: 700;
}
.doc-name--teal {
  color: var(--teal-dark);
}
.doc-name--blue {
  color: #0c447c;
}
.doc-name--purple {
  color: #26215c;
}
.doc-spec {
  font-size: 12px;
  margin-top: 2px;
}
.doc-spec--teal {
  color: var(--teal);
}
.doc-spec--blue {
  color: var(--blue);
}
.doc-spec--purple {
  color: var(--purple);
}
.doc-body {
  padding: 18px 22px;
}
.doc-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.doc-row span {
  font-size: 13px;
  color: var(--muted);
}
.doc-row strong {
  font-size: 13px;
  font-weight: 600;
}
.doc-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
  margin-top: 4px;
}
.stars {
  color: #f59e0b;
  font-size: 13px;
}
.rating-val {
  font-size: 13px;
  font-weight: 700;
}
.rating-cnt {
  font-size: 12px;
  color: var(--muted);
}
.doc-btn {
  display: block;
  text-align: center;
  width: 100%;
  padding: 10px;
  font-size: 13px;
  font-weight: 600;
  border: 1.5px solid var(--teal);
  background: transparent;
  color: var(--teal);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition:
    background 0.15s,
    color 0.15s;
  font-family: inherit;
}
.doc-btn:hover {
  background: var(--teal);
  color: var(--white);
}
.doc-btn--blue {
  border-color: var(--blue);
  color: var(--blue);
}
.doc-btn--blue:hover {
  background: var(--blue);
  color: var(--white);
}
.doc-btn--purple {
  border-color: var(--purple);
  color: var(--purple);
}
.doc-btn--purple:hover {
  background: var(--purple);
  color: var(--white);
}

/* ════════════════════════════════
   TESTIMONIALS
════════════════════════════════ */
.testi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.testi-card {
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  padding: 28px 24px;
  transition: box-shadow 0.2s;
}
.testi-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.07);
}
.testi-stars-top {
  font-size: 14px;
  color: #f59e0b;
  margin-bottom: 14px;
}
.testi-quote {
  font-size: 14px;
  color: var(--slate);
  line-height: 1.75;
  margin-bottom: 20px;
  font-style: italic;
}
.testi-author {
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}
.testi-av {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.testi-name {
  font-size: 13px;
  font-weight: 700;
}
.testi-role {
  font-size: 12px;
  color: var(--muted);
  margin-top: 1px;
}

/* ════════════════════════════════
   CTA BAND
════════════════════════════════ */
.cta-band {
  background: linear-gradient(135deg, var(--teal-light) 0%, #d0f0e4 100%);
  border-top: 1px solid var(--teal-mid);
  border-bottom: 1px solid var(--teal-mid);
  padding: 72px 0;
}
.cta-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}
.cta-text h2 {
  font-size: clamp(22px, 3vw, 32px);
  font-weight: 800;
  color: var(--teal-dark);
  letter-spacing: -0.5px;
  margin-bottom: 10px;
}
.cta-text p {
  font-size: 15px;
  color: var(--teal);
  line-height: 1.7;
  max-width: 480px;
}
.cta-btns {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
}
.cta-btn-primary {
  background: var(--teal-dark);
  justify-content: center;
  font-size: 15px;
  padding: 14px 28px;
}
.cta-btn-primary:hover {
  background: var(--teal-deeper);
}

/* ════════════════════════════════
   FOOTER
════════════════════════════════ */
footer {
  border-top: 1px solid var(--border);
  padding: 56px 0 0;
  background: var(--white);
}
.footer-inner {
  display: grid;
  grid-template-columns: 2.5fr 1fr 1fr 1fr;
  gap: 48px;
  padding-bottom: 48px;
}
.footer-brand .logo {
  font-size: 20px;
  display: block;
  margin-bottom: 10px;
}
.footer-brand p {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.7;
  max-width: 220px;
}
.footer-col h5 {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 14px;
  color: var(--charcoal);
}
.footer-col a {
  display: block;
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 10px;
  transition: color 0.15s;
}
.footer-col a:hover {
  color: var(--teal);
}
.footer-bottom {
  border-top: 1px solid var(--border);
  padding: 20px 48px;
  display: flex;
  justify-content: center;
}
.footer-bottom span {
  font-size: 13px;
  color: var(--muted);
}

/* ════════════════════════════════
   RESPONSIVE
════════════════════════════════ */
@media (max-width: 1024px) {
  .wide-container {
    padding: 0 32px;
  }
  .nav-inner {
    padding: 0 32px;
  }
  .hero-inner {
    padding: 60px 32px 0;
    gap: 40px;
    min-height: auto;
  }
  .spec-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .wide-container {
    padding: 0 20px;
  }
  .nav-inner {
    padding: 0 20px;
  }
  .nav-links {
    display: none;
  }
  .hero-inner {
    grid-template-columns: 1fr;
    padding: 48px 20px 0;
    gap: 32px;
  }
  .hero-visual {
    display: none;
  }
  .hero-text h1 {
    font-size: 36px;
  }
  .stats-inner {
    padding: 0 20px;
    flex-wrap: wrap;
    gap: 24px;
  }
  .stat-item {
    flex: none;
    width: 45%;
    border: none;
  }
  .section {
    padding: 56px 0;
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .section-sub {
    max-width: 100%;
  }
  .steps {
    flex-direction: column;
  }
  .step-arrow {
    transform: rotate(90deg);
    padding: 4px 0;
  }
  .spec-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .features-grid {
    grid-template-columns: 1fr;
  }
  .docs-grid {
    grid-template-columns: 1fr;
  }
  .testi-grid {
    grid-template-columns: 1fr;
  }
  .footer-inner {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
  .cta-inner {
    flex-direction: column;
    gap: 28px;
  }
  .cta-btns {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .footer-bottom {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .spec-grid {
    grid-template-columns: 1fr 1fr;
  }
  .footer-inner {
    grid-template-columns: 1fr;
  }
  .meta-item:first-child {
    padding-left: 0;
  }
}
</style>
