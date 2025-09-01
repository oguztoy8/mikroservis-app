// frontend/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function Dashboard() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    age: '',
    bio: '',
    location: '',
    profession: ''
  });
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [profileId, setProfileId] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [stats, setStats] = useState({
    totalUsers: 0,
    newUsersToday: 0,
    profileCompletion: 0
  });

  useEffect(() => {
    fetchUsers();
    calculateStats();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/users/list`);
      setUsers(response.data);
      
      // Find current user's profile
      const userProfile = response.data.find(u => u.username === user.username);
      if (userProfile) {
        setProfile({
          name: userProfile.name || '',
          email: userProfile.email || '',
          age: userProfile.age || '',
          bio: userProfile.bio || '',
          location: userProfile.location || '',
          profession: userProfile.profession || ''
        });
        setProfileId(userProfile._id);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      showMessage('Failed to load user data', 'error');
    }
  };

  const calculateStats = () => {
    const profileFields = Object.values(profile).filter(value => value && value.trim() !== '');
    const completion = Math.round((profileFields.length / 6) * 100);
    
    const today = new Date().toDateString();
    const newUsersToday = users.filter(user => 
      new Date(user.created_at).toDateString() === today
    ).length;

    setStats({
      totalUsers: users.length,
      newUsersToday,
      profileCompletion: completion
    });
  };

  useEffect(() => {
    calculateStats();
  }, [users, profile]);

  const showMessage = (text, type = 'success', duration = 3000) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(''), duration);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateProfile = () => {
    if (!profile.name.trim()) {
      showMessage('Name is required', 'error');
      return false;
    }
    if (profile.email && !/\S+@\S+\.\S+/.test(profile.email)) {
      showMessage('Please enter a valid email address', 'error');
      return false;
    }
    if (profile.age && (isNaN(profile.age) || profile.age < 1 || profile.age > 150)) {
      showMessage('Please enter a valid age between 1 and 150', 'error');
      return false;
    }
    return true;
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateProfile()) return;

    setLoading(true);

    try {
      const profileData = { 
        ...profile, 
        username: user.username,
        updated_at: new Date().toISOString()
      };
      
      if (profileId) {
        await axios.put(`${API_URL}/users/update/${profileId}`, profileData);
        showMessage('✅ Profile updated successfully!', 'success');
      } else {
        const response = await axios.post(`${API_URL}/users/create`, profileData);
        setProfileId(response.data.id);
        showMessage('✅ Profile created successfully!', 'success');
      }
      
      await fetchUsers();
    } catch (error) {
      console.error('Profile save error:', error);
      showMessage('❌ Failed to save profile. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  const clearMessage = () => {
    setMessage('');
  };

  const getProfileCompletionColor = () => {
    if (stats.profileCompletion >= 80) return '#10b981'; // green
    if (stats.profileCompletion >= 50) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getUserInitials = (name, username) => {
    if (name && name.trim()) {
      const names = name.trim().split(' ');
      return names.length > 1 
        ? `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase()
        : name.charAt(0).toUpperCase();
    }
    return username ? username.charAt(0).toUpperCase() : 'U';
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <div className="header-left">
              <h1>Hello, {profile.name || user.username}! 👋</h1>
              <p>Welcome back to your dashboard</p>
            </div>
            <div className="header-right">
              <button onClick={handleLogout} className="logout-btn">
                <span className="logout-icon">🚪</span>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-content">
                <h3>{stats.totalUsers}</h3>
                <p>Total Users</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">✨</div>
              <div className="stat-content">
                <h3>{stats.newUsersToday}</h3>
                <p>New Today</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <h3>{stats.profileCompletion}%</h3>
                <p>Profile Complete</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: `${stats.profileCompletion}%`,
                      backgroundColor: getProfileCompletionColor()
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="container">
          {/* Message Display */}
          {message && (
            <div className={`message-banner ${message.type}`}>
              <span>{message.text}</span>
              <button onClick={clearMessage} className="message-close">×</button>
            </div>
          )}

          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button 
              className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              📝 My Profile
            </button>
            <button 
              className={`tab-btn ${activeTab === 'community' ? 'active' : ''}`}
              onClick={() => setActiveTab('community')}
            >
              👥 Community
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'profile' && (
              <div className="profile-section">
                <div className="section-card">
                  <div className="card-header">
                    <h2>Edit Profile</h2>
                    <p>Keep your information up to date</p>
                  </div>
                  
                  <form onSubmit={handleProfileSubmit} className="profile-form">
                    <div className="form-grid">
                      <div className="form-group">
                        <label htmlFor="name">
                          Full Name <span className="required">*</span>
                        </label>
                        <input
                          type="text"
                          id="name"
                          name="name"
                          value={profile.name}
                          onChange={handleInputChange}
                          placeholder="Enter your full name"
                          disabled={loading}
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label htmlFor="email">Email Address</label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          value={profile.email}
                          onChange={handleInputChange}
                          placeholder="your.email@example.com"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group">
                        <label htmlFor="age">Age</label>
                        <input
                          type="number"
                          id="age"
                          name="age"
                          value={profile.age}
                          onChange={handleInputChange}
                          placeholder="Your age"
                          disabled={loading}
                          min="1"
                          max="150"
                        />
                      </div>

                      <div className="form-group">
                        <label htmlFor="profession">Profession</label>
                        <input
                          type="text"
                          id="profession"
                          name="profession"
                          value={profile.profession}
                          onChange={handleInputChange}
                          placeholder="What do you do?"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group full-width">
                        <label htmlFor="location">Location</label>
                        <input
                          type="text"
                          id="location"
                          name="location"
                          value={profile.location}
                          onChange={handleInputChange}
                          placeholder="Where are you from?"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group full-width">
                        <label htmlFor="bio">About Me</label>
                        <textarea
                          id="bio"
                          name="bio"
                          value={profile.bio}
                          onChange={handleInputChange}
                          placeholder="Tell us about yourself..."
                          disabled={loading}
                          rows="4"
                        />
                      </div>
                    </div>

                    <div className="form-actions">
                      <button 
                        type="submit" 
                        className="save-btn" 
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <div className="spinner"></div>
                            Saving...
                          </>
                        ) : (
                          <>
                            {profileId ? '💾 Update Profile' : '✨ Create Profile'}
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {activeTab === 'community' && (
              <div className="community-section">
                <div className="section-card">
                  <div className="card-header">
                    <h2>Community Members</h2>
                    <div className="header-actions">
                      <button 
                        onClick={fetchUsers} 
                        className="refresh-btn"
                        disabled={loading}
                      >
                        🔄 Refresh
                      </button>
                    </div>
                  </div>
                  
                  <div className="users-grid">
                    {users.length > 0 ? (
                      users.map((userItem) => (
                        <div key={userItem._id} className="user-card">
                          <div className="user-header">
                            <div className="user-avatar">
                              {getUserInitials(userItem.name, userItem.username)}
                            </div>
                            {userItem.username === user.username && (
                              <div className="user-badge">You</div>
                            )}
                          </div>
                          
                          <div className="user-info">
                            <h3>{userItem.name || userItem.username}</h3>
                            {userItem.profession && (
                              <p className="user-profession">{userItem.profession}</p>
                            )}
                            {userItem.location && (
                              <p className="user-location">📍 {userItem.location}</p>
                            )}
                            {userItem.email && (
                              <p className="user-email">✉️ {userItem.email}</p>
                            )}
                            {userItem.age && (
                              <p className="user-age">🎂 {userItem.age} years old</p>
                            )}
                          </div>

                          {userItem.bio && (
                            <div className="user-bio">
                              <p>"{userItem.bio}"</p>
                            </div>
                          )}

                          <div className="user-footer">
                            <small>
                              📅 Joined {formatDate(userItem.created_at)}
                            </small>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="empty-state">
                        <div className="empty-icon">👻</div>
                        <h3>No users found</h3>
                        <p>Be the first to create a profile!</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;