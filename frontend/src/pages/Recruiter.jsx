import { useEffect, useState } from 'react';
import api from '../services/api';
import BarChart from '../components/BarChart';
import CompanyAvatar from '../components/CompanyAvatar';

const blankJob = {
  company_name: '',
  title: '',
  location: 'Hyderabad',
  salary_min: '400000',
  salary_max: '700000',
  experience: '0–2 years',
  employment_type: 'FULL_TIME',
  work_mode: 'HYBRID',
  industry: 'Technology',
  required_skills: '',
  description: '',
  responsibilities: '',
  qualifications: '',
  hiring_stages: 'Assessment,Technical Interview,HR',
  expected_timeline: '2–3 weeks',
  deadline: '',
  refund_conditions: 'Eligible after attending the hiring process',
};

export default function Recruiter() {
  const [apps, setApps] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [d, setD] = useState({});
  const [filter, setFilter] = useState('');
  const [q, setQ] = useState('');
  const [schedule, setSchedule] = useState(null);
  const [showJob, setShowJob] = useState(false);

  const [form, setForm] = useState({
    date: '',
    time: '',
    interview_type: 'Technical',
    location: '',
    meeting_link: '',
  });

  const [jobForm, setJobForm] = useState({ ...blankJob });
  const [msg, setMsg] = useState('');
  const [posting, setPosting] = useState(false);

  const load = async () => {
    const params = {};

    if (filter === 'PRIORITY') {
      params.priority = 'true';
    } else if (filter) {
      params.status = filter;
    }

    if (q) {
      params.q = q;
    }

    try {
      const [a, b, j] = await Promise.all([
        api.get('/applications/', { params }),
        api.get('/dashboard/'),
        api.get('/recruiter/jobs/'),
      ]);

      setApps(a.data);
      setD(b.data);
      setJobs(j.data);
    } catch (e) {
      setMsg(
        e.response?.data?.detail ||
          'Unable to load recruiter data'
      );
    }
  };

  useEffect(() => {
    load();
  }, [filter]);

  const action = async (id, a) => {
    try {
      await api.patch(`/applications/${id}/action/`, {
        action: a,
      });

      await load();
    } catch (e) {
      setMsg(
        e.response?.data?.detail ||
          'Action failed'
      );
    }
  };

  const outcome = async (id, o) => {
    try {
      await api.patch(`/applications/${id}/outcome/`, {
        outcome: o,
      });

      await load();
    } catch (e) {
      setMsg(
        e.response?.data?.detail ||
          'Outcome update failed'
      );
    }
  };

  const attendance = async (interviewId, s) => {
    try {
      await api.patch(
        `/interviews/${interviewId}/attendance/`,
        {
          status: s,
        }
      );

      await load();
    } catch (e) {
      setMsg(
        e.response?.data?.detail ||
          'Attendance update failed'
      );
    }
  };

  const closeJob = async (id) => {
    if (
      !window.confirm(
        'Close this job? It will stop new applications but keep existing records.'
      )
    ) {
      return;
    }

    try {
      await api.patch(`/jobs/${id}/`, {
        is_open: false,
      });

      await load();
      setMsg('Job closed successfully.');
    } catch (e) {
      setMsg(
        e.response?.data?.detail ||
          'Unable to close job'
      );
    }
  };

  const createInterview = async () => {
    if (!schedule) {
      return;
    }

    if (!form.date || !form.time) {
      setMsg('Please select the interview date and time.');
      return;
    }

    try {
      await api.post('/interviews/', {
        application_id: schedule.id,
        ...form,
      });

      setSchedule(null);

      setForm({
        date: '',
        time: '',
        interview_type: 'Technical',
        location: '',
        meeting_link: '',
      });

      await load();

      setMsg('Interview scheduled successfully.');
    } catch (e) {
      setMsg(
        e.response?.data?.detail ||
          'Could not schedule interview'
      );
    }
  };

  const createJob = async () => {
    if (posting) {
      return;
    }

    setMsg('');

    const min = Number(jobForm.salary_min);
    const max = Number(jobForm.salary_max);

    const skills = jobForm.required_skills
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);

    const stages = jobForm.hiring_stages
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);

    // Frontend validation
    if (!jobForm.company_name.trim()) {
      setMsg('Please enter the company name.');
      return;
    }

    if (!jobForm.title.trim()) {
      setMsg('Please enter the job title.');
      return;
    }

    if (!jobForm.description.trim()) {
      setMsg('Please enter the job description.');
      return;
    }

    if (
      !Number.isFinite(min) ||
      !Number.isFinite(max) ||
      min < 0 ||
      max < 0 ||
      min > max
    ) {
      setMsg('Please enter a valid salary range.');
      return;
    }

    if (!jobForm.location.trim()) {
      setMsg('Please enter the job location.');
      return;
    }

    setPosting(true);

    try {
      const payload = {
        company_name: jobForm.company_name.trim(),
        title: jobForm.title.trim(),
        location: jobForm.location.trim(),

        salary_min: min,
        salary_max: max,

        experience:
          jobForm.experience.trim() || '0–2 years',

        employment_type:
          jobForm.employment_type,

        work_mode:
          jobForm.work_mode,

        industry:
          jobForm.industry.trim() || 'Technology',

        required_skills: skills,

        description:
          jobForm.description.trim(),

        responsibilities:
          jobForm.responsibilities.trim(),

        qualifications:
          jobForm.qualifications.trim(),

        hiring_stages:
          stages.length
            ? stages
            : [
                'Assessment',
                'Technical Interview',
                'HR',
              ],

        expected_timeline:
          jobForm.expected_timeline.trim() ||
          '2–3 weeks',

        deadline:
          jobForm.deadline || null,

        refund_conditions:
          jobForm.refund_conditions.trim() ||
          'Eligible after attending the hiring process',
      };

      const response = await api.post(
        '/recruiter/jobs/',
        payload
      );

      console.log(
        'Job published successfully:',
        response.data
      );

      // Close modal
      setShowJob(false);

      // Reset form
      setJobForm({ ...blankJob });

      // Reload recruiter jobs
      await load();

      // Success message
      setMsg(
        `✓ Job published successfully: ${
          response.data.title || payload.title
        }.`
      );
    } catch (e) {
      console.error(
        'Publish job error:',
        e
      );

      const data = e.response?.data;

      let detail = '';

      if (typeof data === 'string') {
        detail = data;
      } else if (data?.detail) {
        detail = data.detail;
      } else if (data?.message) {
        detail = data.message;
      } else if (data) {
        detail = Object.entries(data)
          .map(([key, value]) => {
            const message = Array.isArray(value)
              ? value.join(', ')
              : String(value);

            return `${key}: ${message}`;
          })
          .join(' | ');
      }

      setMsg(
        detail ||
          'Could not publish job. Please check the form and try again.'
      );
    } finally {
      setPosting(false);
    }
  };

  const funnel = [
    ['Applied', d.total_applications],
    ['Priority', d.priority_applications],
    ['Shortlisted', d.shortlisted],
    ['Interviews', d.interviews],
    ['Selected', d.selected],
  ];

  return (
    <div className="container py-4 py-lg-5">

      {/* RECRUITER HEADER */}
      <div className="dashboard-hero recruiter-hero">
        <div>
          <div className="eyebrow">
            RECRUITER COMMAND CENTER
          </div>

          <h1>
            Hire with evidence, not guesswork.
          </h1>

          <p>
            Priority visibility is separate from candidate suitability.
          </p>
        </div>

        <div className="recruiter-hero-actions">
          <button
            className="btn btn-primary"
            onClick={() => {
              setMsg('');
              setJobForm({ ...blankJob });
              setShowJob(true);
            }}
          >
            + Post a job
          </button>

          <div className="verified-banner">
            ✓ Company tools · Screening · Interviews · Outcomes
          </div>
        </div>
      </div>

      {/* STATS */}
      <div className="row g-3 mb-4">
        {[
          ['Applications', d.total_applications],
          ['Priority', d.priority_applications],
          ['Shortlisted', d.shortlisted],
          ['Interviews', d.interviews],
          ['Selected', d.selected],
          ['Rejected', d.rejected],
        ].map(([label, value]) => (
          <div
            className="col-6 col-lg-2"
            key={label}
          >
            <div className="stat-card-modern">
              <small>{label}</small>
              <strong>{value ?? 0}</strong>
            </div>
          </div>
        ))}
      </div>

      {/* MESSAGE */}
      {msg && (
        <div
          className="alert alert-info"
          role="alert"
        >
          {msg}
        </div>
      )}

      <div className="row g-4">

        {/* APPLICATION PIPELINE */}
        <div className="col-lg-8">
          <div className="page-card">

            <div className="card-head">
              <div>
                <div className="eyebrow">
                  CANDIDATE PIPELINE
                </div>

                <h3>
                  Applications
                </h3>
              </div>

              <div className="search-inline">
                <input
                  placeholder="Search candidate or role"
                  value={q}
                  onChange={(e) =>
                    setQ(e.target.value)
                  }
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      load();
                    }
                  }}
                />

                <button onClick={load}>
                  Search
                </button>
              </div>
            </div>

            {/* FILTERS */}
            <div className="filter-pills">
              {[
                '',
                'PRIORITY',
                'SHORTLISTED',
                'ON_HOLD',
                'REJECTED',
                'SELECTED',
                'NO_SHOW',
              ].map((x) => (
                <button
                  key={x}
                  className={
                    filter === x
                      ? 'active'
                      : ''
                  }
                  onClick={() =>
                    setFilter(x)
                  }
                >
                  {x
                    ? x.replace('_', ' ')
                    : 'ALL'}
                </button>
              ))}
            </div>

            {/* APPLICATION TABLE */}
            <div className="table-responsive">
              <table className="table align-middle recruiter-table">

                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Match</th>
                    <th>Skills</th>
                    <th>Fee</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {apps.map((a) => {
                    const interviewed =
                      [
                        'ATTENDED',
                        'COMPLETED',
                      ].includes(
                        a.interview?.status
                      );

                    return (
                      <tr key={a.id}>

                        <td>
                          <div className="d-flex gap-2 align-items-center">
                            <CompanyAvatar
                              name={a.candidate}
                            />

                            <div>
                              <b>
                                {a.candidate}
                              </b>

                              <div className="small text-secondary">
                                {a.job.title}
                              </div>
                            </div>
                          </div>
                        </td>

                        <td>
                          <strong>
                            {a.match_percent}%
                          </strong>
                        </td>

                        <td>
                          {a.matched_skills?.length || 0}{' '}
                          matched
                        </td>

                        <td>
                          <strong>
                            ₹
                            {Number(
                              a.payment?.amount || 0
                            ).toLocaleString(
                              'en-IN'
                            )}
                          </strong>
                        </td>

                        <td>
                          {a.priority_level ===
                          'PRIORITY' ? (
                            <span className="priority-badge">
                              PRIORITY
                            </span>
                          ) : (
                            <span className="small">
                              NORMAL
                            </span>
                          )}
                        </td>

                        <td>
                          <span className="status-chip">
                            {String(
                              a.status
                            ).replace(
                              '_',
                              ' '
                            )}
                          </span>

                          {a.interview && (
                            <div className="small mt-1">
                              Interview:{' '}
                              {a.interview.date} ·{' '}
                              {a.interview.status}
                            </div>
                          )}

                          {a.refund_status && (
                            <div className="small text-secondary">
                              Refund:{' '}
                              {String(
                                a.refund_status
                              ).replace(
                                '_',
                                ' '
                              )}
                            </div>
                          )}
                        </td>

                        <td className="text-nowrap">

                          <div className="d-flex flex-wrap gap-1">

                            {/* SHORTLIST */}
                            {![
                              'SHORTLISTED',
                              'SELECTED',
                              'REJECTED',
                              'ON_HOLD',
                            ].includes(
                              a.status
                            ) && (
                              <button
                                className="action-link green"
                                onClick={() =>
                                  action(
                                    a.id,
                                    'SHORTLISTED'
                                  )
                                }
                              >
                                Shortlist
                              </button>
                            )}

                            {/* REJECT BEFORE INTERVIEW */}
                            {![
                              'REJECTED',
                              'SELECTED',
                            ].includes(
                              a.status
                            ) && (
                              <button
                                className="action-link red"
                                onClick={() =>
                                  outcome(
                                    a.id,
                                    'REJECTED'
                                  )
                                }
                              >
                                Reject
                              </button>
                            )}

                            {/* SCHEDULE */}
                            {a.status ===
                              'SHORTLISTED' &&
                              !a.interview && (
                                <button
                                  className="action-link blue"
                                  onClick={() =>
                                    setSchedule(a)
                                  }
                                >
                                  Schedule
                                </button>
                            )}

                            {/* ATTENDANCE */}
                            {a.interview?.status ===
                              'SCHEDULED' && (
                                <>
                                  <button
                                    className="action-link green"
                                    onClick={() =>
                                      attendance(
                                        a.interview.id,
                                        'ATTENDED'
                                      )
                                    }
                                  >
                                    Attended
                                  </button>

                                  <button
                                    className="action-link red"
                                    onClick={() =>
                                      attendance(
                                        a.interview.id,
                                        'NO_SHOW'
                                      )
                                    }
                                  >
                                    No-show
                                  </button>
                                </>
                            )}

                            {/* POST-INTERVIEW OUTCOMES */}
                            {interviewed &&
                              a.status !==
                                'SELECTED' &&
                              a.status !==
                                'REJECTED' && (
                                <>
                                  <button
                                    className="action-link dark"
                                    onClick={() =>
                                      outcome(
                                        a.id,
                                        'SELECTED'
                                      )
                                    }
                                  >
                                    Hire
                                  </button>

                                  <button
                                    className="action-link blue"
                                    onClick={() =>
                                      outcome(
                                        a.id,
                                        'ON_HOLD'
                                      )
                                    }
                                  >
                                    On hold
                                  </button>

                                  <button
                                    className="action-link red"
                                    onClick={() =>
                                      outcome(
                                        a.id,
                                        'REJECTED'
                                      )
                                    }
                                  >
                                    Reject
                                  </button>
                                </>
                            )}

                          </div>
                        </td>

                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {!apps.length && (
              <div className="empty">
                No candidates match this filter.
              </div>
            )}

          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="col-lg-4">

          {/* FUNNEL */}
          <div className="page-card mb-4">
            <div className="eyebrow">
              HIRING FUNNEL
            </div>

            <h3>
              Pipeline health
            </h3>

            <BarChart
              data={funnel.map(
                ([label, value]) => ({
                  label,
                  value: value || 0,
                })
              )}
            />
          </div>

          {/* YOUR JOBS */}
          <div className="page-card mb-4">

            <div className="card-head">
              <div>
                <div className="eyebrow">
                  YOUR JOBS
                </div>

                <h3>
                  Published openings
                </h3>
              </div>

              <button
                className="btn btn-sm btn-primary"
                onClick={() => {
                  setMsg('');
                  setJobForm({
                    ...blankJob,
                  });
                  setShowJob(true);
                }}
              >
                Post
              </button>
            </div>

            {jobs.length ? (
              jobs
                .slice(0, 8)
                .map((j) => (
                  <div
                    className="saved-resume"
                    key={j.id}
                  >
                    <div>
                      <b>
                        {j.title}
                      </b>

                      <div className="small text-secondary">
                        {j.company?.name ||
                          'Company'}{' '}
                        · {j.location} ·{' '}
                        {j.job_freshness}
                      </div>
                    </div>

                    <div className="d-flex align-items-center gap-2">

                      <span>
                        {j.is_open
                          ? 'Open'
                          : 'Closed'}
                      </span>

                      {j.is_open && (
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() =>
                            closeJob(j.id)
                          }
                        >
                          Close
                        </button>
                      )}

                    </div>
                  </div>
                ))
            ) : (
              <p className="text-secondary mb-0">
                No jobs posted yet.
              </p>
            )}

          </div>

          {/* INTERVIEW CARD */}
          <div className="feature-card compact">
            <span className="feature-icon">
              ◷
            </span>

            <h5>
              Interview scheduling
            </h5>

            <p>
              Schedule a type, date, time,
              location or meeting link and
              notify the candidate automatically.
            </p>
          </div>

        </div>
      </div>

      {/* INTERVIEW MODAL */}
      {schedule && (
        <div className="modal-backdrop-custom">

          <div className="modal-card">

            <div className="d-flex justify-content-between">

              <div>
                <div className="eyebrow">
                  SCHEDULE INTERVIEW
                </div>

                <h3>
                  {schedule.job.title}
                </h3>

                <p className="text-secondary mb-3">
                  {schedule.candidate}
                </p>
              </div>

              <button
                className="close-btn"
                onClick={() =>
                  setSchedule(null)
                }
              >
                ×
              </button>

            </div>

            <div className="row g-3">

              <div className="col-md-6">
                <label>
                  Date
                </label>

                <input
                  type="date"
                  className="form-control"
                  value={form.date}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      date: e.target.value,
                    })
                  }
                />
              </div>

              <div className="col-md-6">
                <label>
                  Time
                </label>

                <input
                  type="time"
                  className="form-control"
                  value={form.time}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      time: e.target.value,
                    })
                  }
                />
              </div>

              <div className="col-md-6">
                <label>
                  Interview type
                </label>

                <select
                  className="form-select"
                  value={form.interview_type}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      interview_type:
                        e.target.value,
                    })
                  }
                >
                  <option>
                    Technical
                  </option>

                  <option>
                    HR
                  </option>

                  <option>
                    Managerial
                  </option>

                  <option>
                    Assessment
                  </option>
                </select>
              </div>

              <div className="col-md-6">
                <label>
                  Location
                </label>

                <input
                  className="form-control"
                  placeholder="Office / Remote"
                  value={form.location}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      location:
                        e.target.value,
                    })
                  }
                />
              </div>

              <div className="col-12">
                <label>
                  Meeting link
                </label>

                <input
                  className="form-control"
                  placeholder="https://..."
                  value={form.meeting_link}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      meeting_link:
                        e.target.value,
                    })
                  }
                />
              </div>

            </div>

            <button
              className="btn btn-primary w-100 mt-4"
              onClick={createInterview}
            >
              Schedule & notify candidate
            </button>

          </div>
        </div>
      )}

      {/* POST JOB MODAL */}
      {showJob && (
        <div className="modal-backdrop-custom">

          <div className="modal-card post-job-modal">

            <div className="d-flex justify-content-between">

              <div>
                <div className="eyebrow">
                  RECRUITER TOOLS
                </div>

                <h3>
                  Post a new job
                </h3>

                <p className="text-secondary">
                  Publish a transparent opening
                  to the JobPortal marketplace.
                </p>
              </div>

              <button
                className="close-btn"
                onClick={() =>
                  !posting &&
                  setShowJob(false)
                }
              >
                ×
              </button>

            </div>

            <div className="row g-3">

              {/* COMPANY */}
              <div className="col-12">
                <label>
                  Company name
                </label>

                <input
                  className="form-control"
                  value={jobForm.company_name}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      company_name:
                        e.target.value,
                    })
                  }
                  placeholder="e.g. NovaTech Solutions"
                />
              </div>

              {/* TITLE */}
              <div className="col-md-8">
                <label>
                  Job title
                </label>

                <input
                  className="form-control"
                  value={jobForm.title}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      title:
                        e.target.value,
                    })
                  }
                  placeholder="e.g. Backend Engineer"
                />
              </div>

              {/* INDUSTRY */}
              <div className="col-md-4">
                <label>
                  Industry
                </label>

                <input
                  className="form-control"
                  value={jobForm.industry}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      industry:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* LOCATION */}
              <div className="col-md-6">
                <label>
                  Location
                </label>

                <input
                  className="form-control"
                  value={jobForm.location}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      location:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* SALARY MIN */}
              <div className="col-md-3">
                <label>
                  Min salary (₹)
                </label>

                <input
                  type="number"
                  className="form-control"
                  value={jobForm.salary_min}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      salary_min:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* SALARY MAX */}
              <div className="col-md-3">
                <label>
                  Max salary (₹)
                </label>

                <input
                  type="number"
                  className="form-control"
                  value={jobForm.salary_max}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      salary_max:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* EXPERIENCE */}
              <div className="col-md-4">
                <label>
                  Experience
                </label>

                <input
                  className="form-control"
                  value={jobForm.experience}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      experience:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* EMPLOYMENT */}
              <div className="col-md-4">
                <label>
                  Employment type
                </label>

                <select
                  className="form-select"
                  value={
                    jobForm.employment_type
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      employment_type:
                        e.target.value,
                    })
                  }
                >
                  <option value="FULL_TIME">
                    Full Time
                  </option>

                  <option value="PART_TIME">
                    Part Time
                  </option>

                  <option value="CONTRACT">
                    Contract
                  </option>
                </select>
              </div>

              {/* WORK MODE */}
              <div className="col-md-4">
                <label>
                  Work mode
                </label>

                <select
                  className="form-select"
                  value={jobForm.work_mode}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      work_mode:
                        e.target.value,
                    })
                  }
                >
                  <option value="WFO">
                    WFO
                  </option>

                  <option value="HYBRID">
                    Hybrid
                  </option>

                  <option value="REMOTE">
                    Remote
                  </option>
                </select>
              </div>

              {/* SKILLS */}
              <div className="col-12">
                <label>
                  Required skills{' '}
                  <span className="text-secondary">
                    (comma separated)
                  </span>
                </label>

                <input
                  className="form-control"
                  value={
                    jobForm.required_skills
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      required_skills:
                        e.target.value,
                    })
                  }
                  placeholder="Python, Django, SQL"
                />
              </div>

              {/* HIRING STAGES */}
              <div className="col-md-6">
                <label>
                  Hiring stages
                </label>

                <input
                  className="form-control"
                  value={
                    jobForm.hiring_stages
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      hiring_stages:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* TIMELINE */}
              <div className="col-md-6">
                <label>
                  Expected timeline
                </label>

                <input
                  className="form-control"
                  value={
                    jobForm.expected_timeline
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      expected_timeline:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* DEADLINE */}
              <div className="col-md-6">
                <label>
                  Application deadline
                </label>

                <input
                  type="date"
                  className="form-control"
                  value={jobForm.deadline}
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      deadline:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* REFUND */}
              <div className="col-md-6">
                <label>
                  Refund conditions
                </label>

                <input
                  className="form-control"
                  value={
                    jobForm.refund_conditions
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      refund_conditions:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* DESCRIPTION */}
              <div className="col-12">
                <label>
                  Description
                </label>

                <textarea
                  className="form-control"
                  rows="3"
                  value={
                    jobForm.description
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      description:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* RESPONSIBILITIES */}
              <div className="col-12">
                <label>
                  Responsibilities
                </label>

                <textarea
                  className="form-control"
                  rows="2"
                  value={
                    jobForm.responsibilities
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      responsibilities:
                        e.target.value,
                    })
                  }
                />
              </div>

              {/* QUALIFICATIONS */}
              <div className="col-12">
                <label>
                  Qualifications
                </label>

                <textarea
                  className="form-control"
                  rows="2"
                  value={
                    jobForm.qualifications
                  }
                  onChange={(e) =>
                    setJobForm({
                      ...jobForm,
                      qualifications:
                        e.target.value,
                    })
                  }
                />
              </div>

            </div>

            {/* POST JOB MESSAGE */}
            {msg && (
              <div className="alert alert-warning mt-3">
                {msg}
              </div>
            )}

            {/* IMPORTANT:
                Only disable while actually posting.
                Validation happens inside createJob().
            */}
            <button
              type="button"
              className="btn btn-primary w-100 mt-4"
              disabled={posting}
              onClick={createJob}
            >
              {posting
                ? 'Publishing…'
                : 'Publish job'}
            </button>

          </div>
        </div>
      )}

    </div>
  );
}