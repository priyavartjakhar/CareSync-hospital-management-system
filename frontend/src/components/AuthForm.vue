<template>
  <div class="cs-wrap" :class="{ 'theme-admin': role === 'admin' }">

    <nav class="cs-nav">
      <a class="cs-nav-brand" @click.prevent="$router.push('/')">
        <div class="brand-text"><span class="care">Care</span><span class="sync">Sync</span></div>
      </a>
      <div class="cs-nav-actions">
        <button class="cs-nav-btn ghost" @click="$router.push('/')">
          <i class="fa fa-home" aria-hidden="true"></i>
          Home
        </button>
        <button
          v-if="role === 'patient'"
          class="cs-nav-btn solid"
          @click="$router.push(isRegisterPage ? '/patient/login' : '/patient/register')"
        >
          <i :class="isRegisterPage ? 'fa fa-sign-in' : 'fa fa-user-plus'" aria-hidden="true"></i>
          {{ isRegisterPage ? 'Patient Login' : 'Patient Registration' }}
        </button>
      </div>
    </nav>

    <main class="cs-main">
      <div class="cs-card" :style="isRegisterPage ? 'max-width:900px' : ''">
        <div class="cs-card-body">
          <div class="cs-portal-icon" :title="title">
            <i v-if="isRegisterPage" class="fa fa-user-plus portal-fa-icon" aria-hidden="true"></i>
            <font-awesome-icon
              v-else-if="role === 'doctor'"
              :icon="['fas', 'user-md']"
              class="portal-fa-icon"
              aria-hidden="true"
            />
            <span v-else class="portal-icon-svg" aria-hidden="true" v-html="portalIcon"></span>
          </div>
          <h2>{{ title }}</h2>
          <p class="sub">{{ subtitle }}</p>

          <!-- ── LOGIN FORM ── -->
          <form v-if="!isRegisterPage" @submit.prevent="handleLogin">
            <div class="cs-field">
              <label>{{ role === 'admin' ? 'Username' : 'Email Address' }}</label>
              <div class="cs-input-wrap">
                <input v-model.trim="loginForm.identifier" :type="role === 'admin' ? 'text' : 'email'" :placeholder="role === 'admin' ? 'admin' : 'you@example.com'" required />
              </div>
            </div>

            <div class="cs-field">
              <label>Password</label>
              <div class="cs-input-wrap">
                <input v-model="loginForm.password" :type="showPassword ? 'text' : 'password'" placeholder="Enter your password" required />
                <button class="cs-toggle-pass" type="button" @click="showPassword = !showPassword">{{ showPassword ? 'Hide' : 'Show' }}</button>
              </div>
            </div>

            <p v-if="error" class="field-err">{{ error }}</p>
            <button class="cs-btn" :disabled="loading">{{ loading ? 'Signing in...' : loginButtonText }}</button>
          </form>

          <!-- ── REGISTER FORM ── -->
          <form v-else @submit.prevent="handleRegister" novalidate>
            <div class="cs-stepper">
              <div class="cs-step" :class="{ active: registerStep === 1, done: registerStep > 1 }">1. Basic</div>
              <div class="cs-step" :class="{ active: registerStep === 2, done: registerStep > 2 }">2. Health &amp; Profile</div>
              <div class="cs-step" :class="{ active: registerStep === 3 }">3. Security</div>
            </div>
            <p class="cs-step-sub">{{ registerStepSubtitle }}</p>

            <!-- ══ STEP 1 ══ -->
            <div v-show="registerStep === 1">
              <h3 class="cs-section-title">Basic Information</h3>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>First Name <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.firstName" type="text" placeholder="John"
                      :class="{ 'input-error': touched.firstName && !regForm.firstName }" />
                  </div>
                  <span v-if="touched.firstName && !regForm.firstName" class="field-err">Required</span>
                </div>
                <div class="cs-field">
                  <label>Last Name <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.lastName" type="text" placeholder="Doe"
                      :class="{ 'input-error': touched.lastName && !regForm.lastName }" />
                  </div>
                  <span v-if="touched.lastName && !regForm.lastName" class="field-err">Required</span>
                </div>
              </div>

              <div class="cs-field">
                <label>Email Address <span class="req-star">*</span></label>
                <div class="cs-input-wrap">
                  <input
                    v-model.trim="regForm.email"
                    type="email"
                    placeholder="you@example.com"
                    :class="emailInputClass"
                    @blur="touched.email = true"
                    @input="validateEmailLive"
                  />
                  <span v-if="emailStatus === 'checking'" class="val-icon checking"><i class="fa fa-spinner fa-spin"></i></span>
                  <span v-else-if="emailStatus === 'ok'"  class="val-icon ok"><i class="fa fa-check-circle"></i></span>
                  <span v-else-if="emailStatus === 'err'" class="val-icon err"><i class="fa fa-times-circle"></i></span>
                </div>
                <span v-if="touched.email && emailStatus === 'err'" class="field-err">{{ emailMsg }}</span>
                <span v-if="emailStatus === 'checking'" class="field-hint">Checking availability…</span>
              </div>

              <div class="cs-field">
                <label>Phone Number <span class="req-star">*</span></label>
                <div class="cs-input-wrap">
                  <input
                    v-model.trim="regForm.phone"
                    type="tel"
                    placeholder="+91 98765 43210"
                    :class="phoneInputClass"
                    @blur="touched.phone = true"
                    @input="validatePhoneLive"
                  />
                  <span v-if="phoneStatus === 'checking'" class="val-icon checking"><i class="fa fa-spinner fa-spin"></i></span>
                  <span v-else-if="phoneStatus === 'ok'"  class="val-icon ok"><i class="fa fa-check-circle"></i></span>
                  <span v-else-if="phoneStatus === 'err'" class="val-icon err"><i class="fa fa-times-circle"></i></span>
                </div>
                <span v-if="touched.phone && phoneStatus === 'err'" class="field-err">{{ phoneMsg }}</span>
                <span v-if="phoneStatus === 'checking'" class="field-hint">Checking availability…</span>
              </div>

              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Date of Birth <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model="regForm.dob" type="date"
                      :class="{ 'input-error': touched.dob && !regForm.dob }"
                      @blur="touched.dob = true" />
                  </div>
                  <span v-if="touched.dob && !regForm.dob" class="field-err">Required</span>
                </div>
                <div class="cs-field">
                  <label>Gender <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <select v-model="regForm.gender"
                      :class="{ 'input-error': touched.gender && !regForm.gender }"
                      @blur="touched.gender = true">
                      <option value="">Select</option>
                      <option>Male</option>
                      <option>Female</option>
                      <option>Other</option>
                    </select>
                  </div>
                  <span v-if="touched.gender && !regForm.gender" class="field-err">Required</span>
                </div>
              </div>

              <div class="cs-field">
                <label>Address <span class="req-star">*</span></label>
                <div class="cs-input-wrap">
                  <textarea v-model.trim="regForm.address" rows="3" placeholder="Street, City, State, ZIP"
                    :class="{ 'input-error': touched.address && !regForm.address }"
                    @blur="touched.address = true"></textarea>
                </div>
                <span v-if="touched.address && !regForm.address" class="field-err">Required</span>
              </div>

              <h3 class="cs-section-title">Emergency Contact <span class="req-star">*</span></h3>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Contact Name <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.emergencyContactName" type="text" placeholder="Jane Doe"
                      :class="{ 'input-error': touched.emergencyContactName && !regForm.emergencyContactName }"
                      @blur="touched.emergencyContactName = true" />
                  </div>
                  <span v-if="touched.emergencyContactName && !regForm.emergencyContactName" class="field-err">Required</span>
                </div>
                <div class="cs-field">
                  <label>Relationship</label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.emergencyContactRelationship" type="text" placeholder="Spouse, Parent" />
                  </div>
                </div>
              </div>
              <div class="cs-field">
                <label>Contact Phone <span class="req-star">*</span></label>
                <div class="cs-input-wrap">
                  <input v-model.trim="regForm.emergencyContactPhone" type="tel" placeholder="+91 98765 43210"
                    :class="{ 'input-error': touched.emergencyContactPhone && !regForm.emergencyContactPhone }"
                    @blur="touched.emergencyContactPhone = true" />
                </div>
                <span v-if="touched.emergencyContactPhone && !regForm.emergencyContactPhone" class="field-err">Required</span>
              </div>
            </div>

            <!-- ══ STEP 2 ══ -->
            <div v-show="registerStep === 2">
              <h3 class="cs-section-title">Medical Basics</h3>
              <div class="cs-field">
                <label>Known Allergies</label>
                <div class="cs-input-wrap">
                  <textarea v-model.trim="regForm.allergies" rows="2" placeholder="Penicillin, peanuts, etc."></textarea>
                </div>
              </div>
              <div class="cs-field">
                <label>Current Medications</label>
                <div class="cs-input-wrap">
                  <textarea v-model.trim="regForm.medications" rows="2" placeholder="List any ongoing medications"></textarea>
                </div>
              </div>
              <div class="cs-field">
                <label>Existing Conditions</label>
                <div class="cs-input-wrap">
                  <textarea v-model.trim="regForm.conditions" rows="2" placeholder="Diabetes, hypertension, etc."></textarea>
                </div>
              </div>
              <div class="cs-field">
                <label>Primary Physician</label>
                <div class="cs-input-wrap">
                  <input v-model.trim="regForm.primaryPhysician" type="text" placeholder="Dr. Smith" />
                </div>
              </div>

              <h3 class="cs-section-title">Insurance</h3>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Provider</label>
                  <div class="cs-input-wrap"><input v-model.trim="regForm.insuranceProvider" type="text" placeholder="Provider name" /></div>
                </div>
                <div class="cs-field">
                  <label>Policy Number</label>
                  <div class="cs-input-wrap"><input v-model.trim="regForm.insurancePolicyNumber" type="text" placeholder="Policy #" /></div>
                </div>
              </div>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Member ID</label>
                  <div class="cs-input-wrap"><input v-model.trim="regForm.insuranceMemberId" type="text" placeholder="Member ID" /></div>
                </div>
                <div class="cs-field">
                  <label>Coverage Start</label>
                  <div class="cs-input-wrap"><input v-model="regForm.insuranceCoverageStart" type="date" /></div>
                </div>
              </div>

              <h3 class="cs-section-title">Preferences &amp; Accessibility</h3>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Preferred Language <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.preferredLanguage" type="text" placeholder="English"
                      :class="{ 'input-error': touched.preferredLanguage && !regForm.preferredLanguage }"
                      @blur="touched.preferredLanguage = true" />
                  </div>
                  <span v-if="touched.preferredLanguage && !regForm.preferredLanguage" class="field-err">Required</span>
                </div>
                <div class="cs-field">
                  <label>Communication Preference <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <select v-model="regForm.communicationPreferences"
                      :class="{ 'input-error': touched.communicationPreferences && !regForm.communicationPreferences }"
                      @blur="touched.communicationPreferences = true">
                      <option value="">Select</option>
                      <option>Email</option>
                      <option>SMS</option>
                      <option>Phone</option>
                      <option>Email + SMS</option>
                      <option>Any</option>
                    </select>
                  </div>
                  <span v-if="touched.communicationPreferences && !regForm.communicationPreferences" class="field-err">Required</span>
                </div>
              </div>
              <div class="cs-field">
                <label>Accessibility Needs</label>
                <div class="cs-input-wrap">
                  <textarea v-model.trim="regForm.accessibilityNeeds" rows="2" placeholder="Hearing assistance, wheelchair access, etc."></textarea>
                </div>
              </div>

              <h3 class="cs-section-title">Additional Details</h3>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Occupation</label>
                  <div class="cs-input-wrap"><input v-model.trim="regForm.occupation" type="text" placeholder="Occupation" /></div>
                </div>
                <div class="cs-field">
                  <label>Marital Status</label>
                  <div class="cs-input-wrap">
                    <select v-model="regForm.maritalStatus">
                      <option value="">Select</option>
                      <option>Single</option>
                      <option>Married</option>
                      <option>Divorced</option>
                      <option>Widowed</option>
                      <option>Separated</option>
                      <option>Prefer not to say</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Blood Type</label>
                  <div class="cs-input-wrap">
                    <select v-model="regForm.bloodType">
                      <option value="">Select</option>
                      <option>A+</option><option>A-</option>
                      <option>B+</option><option>B-</option>
                      <option>AB+</option><option>AB-</option>
                      <option>O+</option><option>O-</option>
                      <option>Unknown</option>
                    </select>
                  </div>
                </div>
                <div class="cs-field">
                  <label>Pregnancy Status</label>
                  <div class="cs-input-wrap">
                    <select v-model="regForm.pregnancyStatus">
                      <option value="">Select</option>
                      <option>Not pregnant</option>
                      <option>Pregnant</option>
                      <option>Prefer not to say</option>
                      <option>Not applicable</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="cs-field">
                <label>Family Medical History</label>
                <div class="cs-input-wrap">
                  <textarea v-model.trim="regForm.familyHistory" rows="2" placeholder="Heart disease, diabetes, etc."></textarea>
                </div>
              </div>
              <div class="cs-field">
                <label>Preferred Pharmacy</label>
                <div class="cs-input-wrap"><input v-model.trim="regForm.preferredPharmacy" type="text" placeholder="Pharmacy name" /></div>
              </div>

              <h3 class="cs-section-title">Identification <span class="req-star">*</span></h3>
              <div class="cs-field-row">
                <div class="cs-field">
                  <label>Government ID Type <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.governmentIdType" type="text" placeholder="Aadhaar, Passport, etc."
                      :class="{ 'input-error': touched.governmentIdType && !regForm.governmentIdType }"
                      @blur="touched.governmentIdType = true" />
                  </div>
                  <span v-if="touched.governmentIdType && !regForm.governmentIdType" class="field-err">Required</span>
                </div>
                <div class="cs-field">
                  <label>Government ID Number <span class="req-star">*</span></label>
                  <div class="cs-input-wrap">
                    <input v-model.trim="regForm.governmentIdNumber" type="text" placeholder="ID number"
                      :class="{ 'input-error': touched.governmentIdNumber && !regForm.governmentIdNumber }"
                      @blur="touched.governmentIdNumber = true" />
                  </div>
                  <span v-if="touched.governmentIdNumber && !regForm.governmentIdNumber" class="field-err">Required</span>
                </div>
              </div>
            </div>

            <!-- ══ STEP 3 ══ -->
            <div v-show="registerStep === 3">
              <h3 class="cs-section-title">Consents <span class="req-star">*</span></h3>
              <div class="cs-field">
                <label class="cs-checkbox">
                  <input v-model="regForm.consentTelehealth" type="checkbox" />
                  I consent to telehealth services when applicable
                </label>
              </div>
              <div class="cs-field">
                <label class="cs-checkbox">
                  <input v-model="regForm.consentReminders" type="checkbox" />
                  I agree to appointment reminders via my preferred channel
                </label>
              </div>
              <div class="cs-field">
                <label class="cs-checkbox">
                  <input v-model="regForm.consentMarketing" type="checkbox" />
                  I agree to receive wellness updates and announcements
                </label>
              </div>
              <div class="cs-field">
                <label class="cs-checkbox" :class="{ 'consent-required': touched.consentTerms && !regForm.consentTerms }">
                  <input v-model="regForm.consentTerms" type="checkbox" @change="touched.consentTerms = true" />
                  I accept the Terms of Service and Privacy Policy <span class="req-star">*</span>
                </label>
                <span v-if="touched.consentTerms && !regForm.consentTerms" class="field-err">You must accept the Terms &amp; Privacy Policy.</span>
              </div>

              <h3 class="cs-section-title">Account Security</h3>

              <!-- Password field -->
              <div class="cs-field">
                <label>Password <span class="req-star">*</span></label>
                <div class="cs-input-wrap">
                  <input
                    v-model="regForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Min. 8 characters"
                    :class="passwordInputClass"
                    @input="validatePasswordLive"
                    @blur="touched.password = true"
                  />
                  <button class="cs-toggle-pass" type="button" @click="showPassword = !showPassword">{{ showPassword ? 'Hide' : 'Show' }}</button>
                </div>
                <!-- Strength meter -->
                <div v-if="regForm.password" class="pwd-strength-wrap">
                  <div class="pwd-strength-bar">
                    <div class="pwd-strength-fill" :class="passwordStrength.level" :style="{ width: passwordStrength.pct + '%' }"></div>
                  </div>
                  <span class="pwd-strength-label" :class="passwordStrength.level">{{ passwordStrength.label }}</span>
                </div>
                <!-- Checklist -->
                <ul v-if="touched.password || regForm.password" class="pwd-checklist">
                  <li :class="pwdRules.length ? 'ok' : 'fail'"><i :class="pwdRules.length ? 'fa fa-check-circle' : 'fa fa-times-circle'"></i> At least 8 characters</li>
                  <li :class="pwdRules.upper ? 'ok' : 'fail'"><i :class="pwdRules.upper ? 'fa fa-check-circle' : 'fa fa-times-circle'"></i> Uppercase letter</li>
                  <li :class="pwdRules.lower ? 'ok' : 'fail'"><i :class="pwdRules.lower ? 'fa fa-check-circle' : 'fa fa-times-circle'"></i> Lowercase letter</li>
                  <li :class="pwdRules.number ? 'ok' : 'fail'"><i :class="pwdRules.number ? 'fa fa-check-circle' : 'fa fa-times-circle'"></i> Number</li>
                  <li :class="pwdRules.special ? 'ok' : 'fail'"><i :class="pwdRules.special ? 'fa fa-check-circle' : 'fa fa-times-circle'"></i> Special character (!@#$…)</li>
                </ul>
              </div>

              <!-- Confirm Password -->
              <div class="cs-field">
                <label>Confirm Password <span class="req-star">*</span></label>
                <div class="cs-input-wrap">
                  <input
                    v-model="regForm.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="Repeat your password"
                    :class="confirmPasswordInputClass"
                    @input="touched.confirmPassword = true"
                    @blur="touched.confirmPassword = true"
                  />
                  <button class="cs-toggle-pass" type="button" @click="showConfirmPassword = !showConfirmPassword">{{ showConfirmPassword ? 'Hide' : 'Show' }}</button>
                  <span v-if="regForm.confirmPassword && passwordsMatch" class="val-icon ok" style="right:60px"><i class="fa fa-check-circle"></i></span>
                  <span v-else-if="regForm.confirmPassword && !passwordsMatch" class="val-icon err" style="right:60px"><i class="fa fa-times-circle"></i></span>
                </div>
                <span v-if="touched.confirmPassword && regForm.confirmPassword && !passwordsMatch" class="field-err">Passwords do not match.</span>
                <span v-if="touched.confirmPassword && !regForm.confirmPassword" class="field-err">Required</span>
              </div>
            </div>

            <p v-if="error" class="field-err" style="margin-top:8px">{{ error }}</p>
            <div class="cs-step-actions">
              <button v-if="registerStep > 1" type="button" class="cs-btn cs-btn-secondary" @click="prevRegisterStep">Back</button>
              <button v-if="registerStep < 3" type="button" class="cs-btn" @click="nextRegisterStep">Next</button>
              <button v-else class="cs-btn" :disabled="loading">{{ loading ? 'Creating account...' : 'Create Account' }}</button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { authAPI } from '../api/auth.js'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUserMd } from '@fortawesome/free-solid-svg-icons'

library.add(faUserMd)

export default {
  name: 'AuthForm',
  components: { FontAwesomeIcon },
  props: {
    role: {
      type: String,
      required: true,
      validator: v => ['admin', 'doctor', 'patient'].includes(v)
    }
  },
  data() {
    return {
      loading: false,
      error: '',
      showPassword: false,
      showConfirmPassword: false,
      registerStep: 1,

      // Real-time validation state
      emailStatus: '',   // '', 'checking', 'ok', 'err'
      emailMsg: '',
      phoneStatus: '',
      phoneMsg: '',

      // debounce timers
      _emailTimer: null,
      _phoneTimer: null,
      touched: {
        firstName: false, lastName: false,
        email: false, phone: false,
        dob: false, gender: false,
        address: false,
        emergencyContactName: false, emergencyContactPhone: false,
        preferredLanguage: false, communicationPreferences: false,
        governmentIdType: false, governmentIdNumber: false,
        consentTerms: false,
        password: false, confirmPassword: false,
      },

      loginForm: { identifier: '', password: '', remember: false },
      regForm: {
        firstName: '', lastName: '',
        email: '', phone: '',
        dob: '', gender: '',
        address: '',
        emergencyContactName: '', emergencyContactRelationship: '', emergencyContactPhone: '',
        allergies: '', medications: '', conditions: '',
        primaryPhysician: '',
        insuranceProvider: '', insurancePolicyNumber: '', insuranceMemberId: '', insuranceCoverageStart: '',
        preferredLanguage: '', communicationPreferences: '', accessibilityNeeds: '',
        occupation: '', maritalStatus: '', bloodType: '', familyHistory: '',
        pregnancyStatus: '', preferredPharmacy: '',
        consentTelehealth: false, consentReminders: false, consentMarketing: false, consentTerms: false,
        governmentIdType: '', governmentIdNumber: '',
        password: '', confirmPassword: ''
      }
    }
  },
  computed: {
    isRegisterPage() {
      return this.role === 'patient' && this.$route.path === '/patient/register'
    },
    /* ── password rules ── */
    pwdRules() {
      const p = this.regForm.password
      return {
        length:  p.length >= 8,
        upper:   /[A-Z]/.test(p),
        lower:   /[a-z]/.test(p),
        number:  /\d/.test(p),
        special: /[^A-Za-z0-9]/.test(p)
      }
    },
    passwordStrength() {
      const r = this.pwdRules
      const score = [r.length, r.upper, r.lower, r.number, r.special].filter(Boolean).length
      if (score <= 1) return { level: 'weak',   label: 'Weak',      pct: 20  }
      if (score === 2) return { level: 'fair',   label: 'Fair',      pct: 40  }
      if (score === 3) return { level: 'good',   label: 'Good',      pct: 65  }
      if (score === 4) return { level: 'strong', label: 'Strong',    pct: 85  }
      return              { level: 'great',  label: 'Very Strong', pct: 100 }
    },
    passwordsMatch() {
      return this.regForm.password && this.regForm.confirmPassword === this.regForm.password
    },
    passwordInputClass() {
      if (!this.touched.password && !this.regForm.password) return ''
      if (this.isStrongPassword(this.regForm.password)) return 'input-ok'
      return 'input-error'
    },
    confirmPasswordInputClass() {
      if (!this.touched.confirmPassword || !this.regForm.confirmPassword) return ''
      return this.passwordsMatch ? 'input-ok' : 'input-error'
    },
    emailInputClass() {
      if (!this.touched.email) return ''
      if (this.emailStatus === 'ok')  return 'input-ok'
      if (this.emailStatus === 'err') return 'input-error'
      return ''
    },
    phoneInputClass() {
      if (!this.touched.phone) return ''
      if (this.phoneStatus === 'ok')  return 'input-ok'
      if (this.phoneStatus === 'err') return 'input-error'
      return ''
    },
    portalIcon() {
      if (this.role === 'admin') {
        return '<svg viewBox="0 0 16 16" width="22" height="22" fill="currentColor"><path d="M5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.78 11.78 0 0 1-2.517 2.453 7.16 7.16 0 0 1-1.048.625c-.281.132-.581.24-.829.24s-.548-.108-.829-.24a7.16 7.16 0 0 1-1.048-.625 11.78 11.78 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.14 2.692A1.54 1.54 0 0 1 2.185 1.43 62.46 62.46 0 0 1 5.072.56"/><path d="M8 4.5a.5.5 0 0 1 .5.5V7h2a.5.5 0 0 1 0 1h-2v2a.5.5 0 0 1-1 0V8h-2a.5.5 0 0 1 0-1h2V5a.5.5 0 0 1 .5-.5"/></svg>'
      }
      if (this.role === 'doctor') {
        return '<svg viewBox="0 0 16 16" width="22" height="22" fill="currentColor"><path d="M5 3a1 1 0 0 1-1-1V1h1v1h1V1h1v1a1 1 0 0 1-1 1v3a3 3 0 0 1-6 0V3zm-1 1v2a2 2 0 1 0 4 0V4z"/><path d="M8.5 5a.5.5 0 0 1 .5.5V8a3 3 0 1 0 6 0V7h-1a1 1 0 1 1 0-2h1a2 2 0 1 1 0 4v1a4 4 0 1 1-8 0V5.5a.5.5 0 0 1 .5-.5"/></svg>'
      }
      if (this.isRegisterPage) {
        return '<svg viewBox="0 0 16 16" width="22" height="22" fill="currentColor"><path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5zM13 2.5 10.5 0v2a.5.5 0 0 0 .5.5z"/><path d="M8.5 6a.5.5 0 0 1 .5.5V8h1.5a.5.5 0 0 1 0 1H9v1.5a.5.5 0 0 1-1 0V9H6.5a.5.5 0 0 1 0-1H8V6.5a.5.5 0 0 1 .5-.5"/></svg>'
      }
      return '<svg viewBox="0 0 16 16" width="22" height="22" fill="currentColor"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/><path d="M14 14s-1-4-6-4-6 4-6 4 1 2 6 2 6-2 6-2"/></svg>'
    },
    title() {
      if (this.isRegisterPage) return 'Create Your Account'
      if (this.role === 'admin') return 'Admin Dashboard Login'
      if (this.role === 'doctor') return 'Doctor Portal Login'
      return 'Patient Login'
    },
    subtitle() {
      if (this.isRegisterPage) return 'Join CareSync to book appointments and manage health records.'
      if (this.role === 'admin') return 'Hospital management system administration.'
      if (this.role === 'doctor') return 'Access your appointments and patient records.'
      return 'Access your appointments and health records.'
    },
    loginButtonText() {
      if (this.role === 'admin') return 'Sign In to Dashboard'
      if (this.role === 'doctor') return 'Sign In to Portal'
      return 'Sign In'
    },
    registerStepSubtitle() {
      if (this.registerStep === 1) return 'Tell us who you are and how to reach you.'
      if (this.registerStep === 2) return 'Add medical, insurance, preference and identification details.'
      return 'Set your account password and consent preferences.'
    }
  },
  methods: {
    /* ── real-time email validation with DB check ── */
    validateEmailLive() {
      this.touched.email = true
      const email = this.regForm.email
      if (!email) {
        this.emailStatus = 'err'
        this.emailMsg = 'Email is required.'
        clearTimeout(this._emailTimer)
        return
      }
      const formatValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
      if (!formatValid) {
        this.emailStatus = 'err'
        this.emailMsg = 'Enter a valid email address.'
        clearTimeout(this._emailTimer)
        return
      }
      // Format OK — debounce DB check
      this.emailStatus = 'checking'
      this.emailMsg = ''
      clearTimeout(this._emailTimer)
      this._emailTimer = setTimeout(async () => {
        try {
          const res = await authAPI.check({ email })
          if (res.email_taken) {
            this.emailStatus = 'err'
            this.emailMsg = 'This email is already registered. Please log in or use a different email.'
          } else {
            this.emailStatus = 'ok'
            this.emailMsg = ''
          }
        } catch {
          // Network error — treat as format-valid to not block the user
          this.emailStatus = 'ok'
          this.emailMsg = ''
        }
      }, 500)
    },
    /* ── real-time phone validation with DB check ── */
    validatePhoneLive() {
      this.touched.phone = true
      const raw = this.regForm.phone.replace(/[\s\-().+]/g, '')
      if (!raw) {
        this.phoneStatus = 'err'
        this.phoneMsg = 'Phone number is required.'
        clearTimeout(this._phoneTimer)
        return
      }
      if (!/^\d{10,13}$/.test(raw)) {
        this.phoneStatus = 'err'
        this.phoneMsg = 'Enter a valid phone number (10–13 digits).'
        clearTimeout(this._phoneTimer)
        return
      }
      // Format OK — debounce DB check
      this.phoneStatus = 'checking'
      this.phoneMsg = ''
      clearTimeout(this._phoneTimer)
      this._phoneTimer = setTimeout(async () => {
        try {
          const res = await authAPI.check({ phone: this.regForm.phone })
          if (res.phone_taken) {
            this.phoneStatus = 'err'
            this.phoneMsg = 'This phone number is already registered. Please use a different number.'
          } else {
            this.phoneStatus = 'ok'
            this.phoneMsg = ''
          }
        } catch {
          this.phoneStatus = 'ok'
          this.phoneMsg = ''
        }
      }, 500)
    },
    /* ── real-time password rules watcher ── */
    validatePasswordLive() {
      this.touched.password = true
    },
    isStrongPassword(password) {
      const p = String(password || '')
      return p.length >= 8 && /[a-z]/.test(p) && /[A-Z]/.test(p) && /\d/.test(p) && /[^A-Za-z0-9]/.test(p)
    },
    /* ── login ── */
    async handleLogin() {
      this.error = ''
      this.loading = true
      try {
        const payload = { password: this.loginForm.password, remember: this.loginForm.remember }
        if (this.role === 'admin') payload.username = this.loginForm.identifier
        else payload.email = this.loginForm.identifier
        const res = await authAPI.login(this.role, payload)
        localStorage.setItem('hms_token', res.token)
        localStorage.setItem('hms_role', res.role)
        localStorage.setItem('hms_user', JSON.stringify(res.user))
        const redirects = { admin: '/admin/dashboard', doctor: '/doctor/dashboard', patient: '/patient/dashboard' }
        await this.$router.push(redirects[this.role])
      } catch (err) {
        this.error = err.message || 'Login failed. Please check your credentials.'
      } finally {
        this.loading = false
      }
    },
    /* ── register ── */
    async handleRegister() {
      this.error = ''
      // Touch all step-3 required fields so errors show
      this.touched.consentTerms = true
      this.touched.password     = true
      this.touched.confirmPassword = true
      if (!this.validateRegisterStep(1)) { this.registerStep = 1; return }
      if (!this.validateRegisterStep(2)) { this.registerStep = 2; return }
      if (!this.validateRegisterStep(3)) return
      if (!this.passwordsMatch) { this.error = 'Passwords do not match.'; return }
      this.loading = true
      try {
        await authAPI.register({
          first_name: this.regForm.firstName,
          last_name:  this.regForm.lastName,
          email:      this.regForm.email,
          phone:      this.regForm.phone,
          dob:        this.regForm.dob,
          gender:     this.regForm.gender,
          address:    this.regForm.address,
          emergency_contact_name:         this.regForm.emergencyContactName,
          emergency_contact_relationship: this.regForm.emergencyContactRelationship,
          emergency_contact_phone:        this.regForm.emergencyContactPhone,
          allergies:   this.regForm.allergies,
          medications: this.regForm.medications,
          conditions:  this.regForm.conditions,
          primary_physician:         this.regForm.primaryPhysician,
          insurance_provider:        this.regForm.insuranceProvider,
          insurance_policy_number:   this.regForm.insurancePolicyNumber,
          insurance_member_id:       this.regForm.insuranceMemberId,
          insurance_coverage_start:  this.regForm.insuranceCoverageStart,
          preferred_language:         this.regForm.preferredLanguage,
          communication_preferences:  this.regForm.communicationPreferences,
          accessibility_needs:        this.regForm.accessibilityNeeds,
          occupation:      this.regForm.occupation,
          marital_status:  this.regForm.maritalStatus,
          blood_type:      this.regForm.bloodType,
          family_history:  this.regForm.familyHistory,
          pregnancy_status: this.regForm.pregnancyStatus,
          preferred_pharmacy: this.regForm.preferredPharmacy,
          consent_telehealth: this.regForm.consentTelehealth,
          consent_reminders:  this.regForm.consentReminders,
          consent_marketing:  this.regForm.consentMarketing,
          consent_terms:      this.regForm.consentTerms,
          government_id_type:   this.regForm.governmentIdType,
          government_id_number: this.regForm.governmentIdNumber,
          password: this.regForm.password
        })
        this.loading = false
        this.error = ''
        this.registerStep = 1
        await this.$router.push('/patient/login')
      } catch (err) {
        this.error = err.message || 'Registration failed.'
      } finally {
        this.loading = false
      }
    },
    validateRegisterStep(step) {
      if (step === 1) {
        // touch all step-1 fields
        Object.assign(this.touched, {
          firstName: true, lastName: true,
          email: true, phone: true,
          dob: true, gender: true, address: true,
          emergencyContactName: true, emergencyContactPhone: true
        })
        // Trigger live checks so statuses update even if user never blurred
        this.validateEmailLive()
        this.validatePhoneLive()
        if (!this.regForm.firstName.trim() || !this.regForm.lastName.trim()) {
          this.error = 'First name and last name are required.'; return false
        }
        if (this.emailStatus === 'checking' || this.phoneStatus === 'checking') {
          this.error = 'Please wait — checking availability…'; return false
        }
        if (this.emailStatus !== 'ok') {
          this.error = this.emailMsg || 'Valid email is required.'; return false
        }
        if (this.phoneStatus !== 'ok') {
          this.error = this.phoneMsg || 'Valid phone number is required.'; return false
        }
        if (!this.regForm.dob)    { this.error = 'Date of birth is required.'; return false }
        if (!this.regForm.gender) { this.error = 'Gender is required.'; return false }
        if (!this.regForm.address.trim()) { this.error = 'Address is required.'; return false }
        if (!this.regForm.emergencyContactName.trim())  { this.error = 'Emergency contact name is required.'; return false }
        if (!this.regForm.emergencyContactPhone.trim()) { this.error = 'Emergency contact phone is required.'; return false }
      }
      if (step === 2) {
        Object.assign(this.touched, {
          preferredLanguage: true, communicationPreferences: true,
          governmentIdType: true, governmentIdNumber: true
        })
        if (!this.regForm.preferredLanguage.trim())    { this.error = 'Preferred language is required.'; return false }
        if (!this.regForm.communicationPreferences)    { this.error = 'Communication preference is required.'; return false }
        if (!this.regForm.governmentIdType.trim())     { this.error = 'Government ID type is required.'; return false }
        if (!this.regForm.governmentIdNumber.trim())   { this.error = 'Government ID number is required.'; return false }
      }
      if (step === 3) {
        if (!this.isStrongPassword(this.regForm.password)) {
          this.error = 'Use a strong password: at least 8 characters with uppercase, lowercase, number, and special character.'
          return false
        }
        if (!this.regForm.confirmPassword || !this.passwordsMatch) {
          this.error = 'Passwords do not match.'; return false
        }
        if (!this.regForm.consentTerms) {
          this.error = 'You must accept the Terms and Privacy Policy.'; return false
        }
      }
      this.error = ''
      return true
    },
    nextRegisterStep() {
      if (!this.validateRegisterStep(this.registerStep)) return
      if (this.registerStep < 3) this.registerStep += 1
    },
    prevRegisterStep() {
      this.error = ''
      if (this.registerStep > 1) this.registerStep -= 1
    }
  }
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css');

* { box-sizing: border-box; margin: 0; padding: 0; }
.cs-wrap { font-family: Arial, Helvetica, sans-serif; background: #F0FDF8; min-height: 100vh; display: flex; flex-direction: column; }
.cs-nav { background: #059669; padding: 0 2rem; height: 56px; display: flex; align-items: center; justify-content: space-between; }
.cs-nav-brand { display: flex; align-items: center; gap: 8px; text-decoration: none; cursor: pointer; }
.cs-nav-brand .brand-text { font-size: 17px; font-weight: 600; letter-spacing: -0.01em; }
.cs-nav-brand .care { color: #fff; }
.cs-nav-brand .sync { color: #A7F3D0; }
.cs-nav-actions { display: flex; gap: 8px; }
.cs-nav-btn { padding: 6px 14px; border-radius: 7px; font-size: 13px; font-weight: 500; cursor: pointer; border: none; }
.cs-nav-btn.ghost { background: rgba(255,255,255,0.12); color: #fff; border: 1px solid rgba(255,255,255,0.25); }
.cs-nav-btn.solid { background: #fff; color: #059669; }
.cs-main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 2.5rem 1rem; }
.cs-card { background: #fff; border-radius: 16px; border: 1px solid #D1FAE5; box-shadow: 0 2px 20px rgba(5,150,105,0.08); width: 100%; max-width: 420px; overflow: hidden; }
.cs-card-body { padding: 2rem; }
.cs-portal-icon { width: 48px; height: 48px; background: #ECFDF5; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; }
.portal-icon-svg { line-height: 0; color: #059669; display: inline-flex; align-items: center; justify-content: center; }
.portal-fa-icon { color: #059669; font-size: 20px; }
.cs-card-body h2 { font-size: 20px; font-weight: 600; color: #0F172A; margin-bottom: 4px; }
.cs-card-body p.sub { font-size: 13px; color: #64748B; margin-bottom: 1.5rem; line-height: 1.5; }

/* Required star */
.req-star { color: #E53E3E; font-weight: 700; margin-left: 2px; }

.cs-field { margin-bottom: 14px; }
.cs-field label { display: block; font-size: 12px; font-weight: 500; color: #475569; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.04em; }
.cs-input-wrap { position: relative; display: flex; align-items: center; }
.cs-input-wrap input,
.cs-input-wrap select,
.cs-input-wrap textarea {
  width: 100%; padding: 9px 11px; font-size: 14px; line-height: 1.35;
  border: 1.5px solid #E2E8F0; border-radius: 8px;
  background: #F8FAFC; color: #0F172A;
  outline: none; transition: border-color 0.15s, box-shadow 0.15s;
  -webkit-appearance: none;
}
.cs-input-wrap select {
  min-height: 38px; box-sizing: border-box; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 16 16'%3E%3Cpath fill='%2394A3B8' d='M8 11L3 6h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 11px center; padding-right: 2rem;
}
.cs-input-wrap textarea { resize: vertical; min-height: 70px; }
.cs-input-wrap input:focus,
.cs-input-wrap select:focus,
.cs-input-wrap textarea:focus { border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,0.1); background: #fff; }

/* Validation border states */
.input-error { border-color: #FC8181 !important; background: #FFF5F5 !important; }
.input-ok    { border-color: #68D391 !important; background: #F0FFF4 !important; }

/* Validation icons */
.val-icon { position: absolute; right: 11px; font-size: 14px; pointer-events: none; }
.val-icon.ok       { color: #38A169; }
.val-icon.err      { color: #E53E3E; }
.val-icon.checking { color: #718096; }
.field-hint { display: block; font-size: 11px; color: #718096; margin-top: 3px; font-style: italic; }

.cs-toggle-pass { position: absolute; right: 10px; background: none; border: none; cursor: pointer; color: #94A3B8; font-size: 11px; z-index: 1; }

/* Password strength meter */
.pwd-strength-wrap { margin-top: 7px; display: flex; align-items: center; gap: 8px; }
.pwd-strength-bar { flex: 1; height: 5px; background: #E2E8F0; border-radius: 99px; overflow: hidden; }
.pwd-strength-fill { height: 100%; border-radius: 99px; transition: width 0.3s, background 0.3s; }
.pwd-strength-fill.weak   { background: #FC8181; }
.pwd-strength-fill.fair   { background: #F6AD55; }
.pwd-strength-fill.good   { background: #F6E05E; }
.pwd-strength-fill.strong { background: #68D391; }
.pwd-strength-fill.great  { background: #38A169; }
.pwd-strength-label { font-size: 11px; font-weight: 700; min-width: 60px; text-align: right; }
.pwd-strength-label.weak   { color: #E53E3E; }
.pwd-strength-label.fair   { color: #DD6B20; }
.pwd-strength-label.good   { color: #B7791F; }
.pwd-strength-label.strong { color: #276749; }
.pwd-strength-label.great  { color: #22543D; }

/* Password checklist */
.pwd-checklist { list-style: none; margin-top: 7px; display: flex; flex-direction: column; gap: 3px; }
.pwd-checklist li { font-size: 11px; display: flex; align-items: center; gap: 5px; }
.pwd-checklist li.ok   { color: #38A169; }
.pwd-checklist li.fail { color: #A0AEC0; }

.cs-field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.cs-btn { width: 100%; padding: 11px; font-size: 14px; font-weight: 600; background: #059669; color: #fff; border: none; border-radius: 9px; cursor: pointer; margin-top: 6px; }
.cs-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.cs-btn-secondary { background: #e2e8f0; color: #0f172a; }
.cs-section-title { font-size: 13px; font-weight: 700; color: #0F172A; margin: 16px 0 10px; text-transform: uppercase; letter-spacing: 0.06em; }
.cs-checkbox { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #334155; text-transform: none; letter-spacing: 0; font-weight: 500; cursor: pointer; }
.cs-checkbox.consent-required { color: #E53E3E; }
.cs-checkbox input { width: 16px; height: 16px; flex-shrink: 0; }
.cs-stepper { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.cs-step { font-size: 12px; padding: 6px 10px; border-radius: 999px; border: 1px solid #d1fae5; background: #f8fafc; color: #64748b; font-weight: 600; }
.cs-step.active { background: #ecfdf5; color: #047857; border-color: #a7f3d0; }
.cs-step.done   { background: #dcfce7; color: #065f46; border-color: #86efac; }
.cs-step-sub { font-size: 12px; color: #64748b; margin-bottom: 14px; }
.cs-step-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; }
.cs-step-actions .cs-btn:only-child { grid-column: 2 / 3; }
.field-err { display: block; font-size: 11px; color: #E53E3E; margin-top: 3px; }

/* Admin theme */
.theme-admin .cs-nav { background: #B83C1F; }
.theme-admin .cs-nav-brand .sync { color: #FED7AA; }
.theme-admin .cs-nav-btn.solid { color: #B83C1F; }
.theme-admin .cs-wrap { background: #FFF8F6; }
.theme-admin .cs-card { border-color: #FECACA; box-shadow: 0 2px 20px rgba(185,28,28,0.07); }
.theme-admin .cs-portal-icon { background: #FEF2F2; }
.theme-admin .portal-icon-svg { color: #B83C1F; }
.theme-admin .portal-fa-icon { color: #B83C1F; }
.theme-admin .cs-input-wrap input:focus,
.theme-admin .cs-input-wrap select:focus,
.theme-admin .cs-input-wrap textarea:focus { border-color: #E05B3A; box-shadow: 0 0 0 3px rgba(224,91,58,0.1); }
.theme-admin .cs-btn { background: #E05B3A; }
.theme-admin .cs-btn-secondary { background: #fee2e2; color: #7f1d1d; }
.theme-admin .cs-step { border-color: #fecaca; }
.theme-admin .cs-step.active { background: #fff1eb; color: #9a3412; border-color: #fdba74; }
.theme-admin .cs-step.done   { background: #ffedd5; color: #9a3412; border-color: #fdba74; }

@media (max-width: 768px) {
  .cs-field-row { grid-template-columns: 1fr; gap: 0; }
  .cs-step-actions { grid-template-columns: 1fr; }
  .cs-step-actions .cs-btn:only-child { grid-column: auto; }
}
</style>
