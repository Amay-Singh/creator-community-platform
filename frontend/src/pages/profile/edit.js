import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import FormGroup from '../../components/ui/FormGroup';
import Card from '../../components/ui/Card';
import Avatar from '../../components/ui/Avatar';

export default function ProfileEdit() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    bio: '',
    location: '',
    skills: '',
    categories: '',
    languages: '',
    portfolioUrl: ''
  });

  useEffect(() => {
    // Load existing profile data
    if (user) {
      setFormData({
        name: user.name || '',
        username: user.username || '',
        bio: user.bio || '',
        location: user.location || '',
        skills: user.skills?.join(', ') || '',
        categories: user.categories?.join(', ') || '',
        languages: user.languages?.join(', ') || '',
        portfolioUrl: user.portfolioUrl || ''
      });
    }
  }, [user]);

  const handleInputChange = (field) => (e) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Transform comma-separated strings back to arrays
      const profileData = {
        ...formData,
        skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean),
        categories: formData.categories.split(',').map(s => s.trim()).filter(Boolean),
        languages: formData.languages.split(',').map(s => s.trim()).filter(Boolean)
      };

      console.log('Profile updated:', profileData);
      router.push('/dashboard');
    } catch (error) {
      console.error('Profile update failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Edit Profile - Creator Community Platform</title>
        <meta name="description" content="Edit your creator profile" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-[var(--color-neutral-50)]">
        {/* Header */}
        <header className="bg-white border-b border-[var(--color-neutral-200)]">
          <div className="max-w-4xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-4)]">
            <div className="flex items-center justify-between">
              <h1 className="text-[var(--font-size-2xl)] font-bold text-[var(--color-neutral-900)]">
                Edit Profile
              </h1>
              <Button
                variant="ghost"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
            </div>
          </div>
        </header>

        <div className="max-w-4xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-8)]">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-[var(--spacing-8)]">
              {/* Profile Picture Section */}
              <div className="lg:col-span-1">
                <Card padding="lg">
                  <h2 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-6)]">
                    Profile Picture
                  </h2>
                  
                  <div className="text-center">
                    <div className="relative inline-block mb-[var(--spacing-4)]">
                      <Avatar 
                        src={user?.avatar} 
                        alt={formData.name || 'Profile'}
                        size="2xl"
                      />
                      <button
                        type="button"
                        className="absolute -bottom-2 -right-2 w-8 h-8 bg-[var(--color-primary-600)] text-white rounded-[var(--radius-full)] flex items-center justify-center hover:bg-[var(--color-primary-700)] transition-colors duration-[var(--duration-fast)]"
                        aria-label="Change profile picture"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </button>
                    </div>
                    
                    <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-600)] mb-[var(--spacing-4)]">
                      Upload a new profile picture to help others recognize you
                    </p>
                    
                    <Button variant="secondary" size="sm">
                      Upload Photo
                    </Button>
                  </div>
                </Card>
              </div>

              {/* Profile Information */}
              <div className="lg:col-span-2">
                <Card padding="lg">
                  <h2 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-6)]">
                    Profile Information
                  </h2>
                  
                  <div className="space-y-[var(--spacing-6)]">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--spacing-4)]">
                      <FormGroup>
                        <Input
                          label="Full Name"
                          value={formData.name}
                          onChange={handleInputChange('name')}
                          placeholder="Enter your full name"
                          required
                        />
                      </FormGroup>
                      
                      <FormGroup>
                        <Input
                          label="Username"
                          value={formData.username}
                          onChange={handleInputChange('username')}
                          placeholder="Choose a unique username"
                          required
                        />
                      </FormGroup>
                    </div>

                    <FormGroup>
                      <label className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-2)]">
                        Bio
                      </label>
                      <textarea
                        value={formData.bio}
                        onChange={handleInputChange('bio')}
                        placeholder="Tell others about yourself and your creative work..."
                        rows={4}
                        className="w-full px-[var(--spacing-4)] py-[var(--spacing-3)] border border-[var(--color-neutral-300)] rounded-[var(--radius-lg)] text-[var(--font-size-base)] text-[var(--color-neutral-900)] placeholder-[var(--color-neutral-500)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)] focus:border-transparent resize-vertical min-h-[100px]"
                      />
                    </FormGroup>

                    <FormGroup>
                      <Input
                        label="Location"
                        value={formData.location}
                        onChange={handleInputChange('location')}
                        placeholder="City, State/Country"
                        helperText="Help others find local collaborators"
                      />
                    </FormGroup>

                    <FormGroup>
                      <Input
                        label="Skills"
                        value={formData.skills}
                        onChange={handleInputChange('skills')}
                        placeholder="Digital Art, Music Production, Writing..."
                        helperText="Separate multiple skills with commas"
                      />
                    </FormGroup>

                    <FormGroup>
                      <Input
                        label="Categories"
                        value={formData.categories}
                        onChange={handleInputChange('categories')}
                        placeholder="Digital Art, Music, Writing, Photography..."
                        helperText="Main creative categories you work in"
                      />
                    </FormGroup>

                    <FormGroup>
                      <Input
                        label="Languages"
                        value={formData.languages}
                        onChange={handleInputChange('languages')}
                        placeholder="English, Spanish, French..."
                        helperText="Languages you can communicate in"
                      />
                    </FormGroup>

                    <FormGroup>
                      <Input
                        label="Portfolio URL"
                        value={formData.portfolioUrl}
                        onChange={handleInputChange('portfolioUrl')}
                        placeholder="https://yourportfolio.com"
                        helperText="Link to your external portfolio or website"
                      />
                    </FormGroup>
                  </div>
                </Card>

                {/* Portfolio Items Section */}
                <Card padding="lg" className="mt-[var(--spacing-8)]">
                  <div className="flex items-center justify-between mb-[var(--spacing-6)]">
                    <h2 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)]">
                      Portfolio Items
                    </h2>
                    <Button variant="secondary" size="sm">
                      Add Item
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[var(--spacing-4)]">
                    {/* Placeholder for portfolio items */}
                    <div className="aspect-square border-2 border-dashed border-[var(--color-neutral-300)] rounded-[var(--radius-lg)] flex flex-col items-center justify-center text-[var(--color-neutral-500)] hover:border-[var(--color-primary-400)] hover:text-[var(--color-primary-600)] transition-colors duration-[var(--duration-fast)] cursor-pointer">
                      <svg className="w-12 h-12 mb-[var(--spacing-2)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <span className="text-[var(--font-size-sm)] font-medium">Add Portfolio Item</span>
                    </div>
                  </div>
                </Card>

                {/* Save Actions */}
                <div className="flex items-center justify-end space-x-[var(--spacing-4)] mt-[var(--spacing-8)]">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => router.back()}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={loading}
                  >
                    Save Changes
                  </Button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
