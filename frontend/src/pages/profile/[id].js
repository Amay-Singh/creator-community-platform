import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import clsx from 'clsx';
import { useAuth } from '../../contexts/AuthContext';
import Avatar from '../../components/ui/Avatar';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';

export default function ProfileView() {
  const router = useRouter();
  const { id } = router.query;
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('about');
  const [loading, setLoading] = useState(true);

  // Mock profile data
  const mockProfile = {
    id: 1,
    name: 'Alex Chen',
    username: 'alexcreates',
    bio: 'Digital artist specializing in character design and concept art for games and animation. I love bringing stories to life through visual storytelling.',
    avatar: null,
    location: 'San Francisco, CA',
    skills: ['Digital Art', 'Character Design', 'Concept Art', 'Illustration'],
    categories: ['Digital Art', 'Gaming'],
    languages: ['English', 'Spanish', 'Mandarin'],
    rating: 4.8,
    reviewCount: 127,
    isOnline: true,
    portfolioItems: [
      { id: 1, type: 'image', title: 'Fantasy Character Set', url: '/mock-image-1.jpg' },
      { id: 2, type: 'image', title: 'Cyberpunk Concepts', url: '/mock-image-2.jpg' },
      { id: 3, type: 'video', title: 'Process Video', url: '/mock-video-1.mp4' }
    ],
    links: [
      { platform: 'Instagram', url: 'https://instagram.com/alexcreates', verified: true },
      { platform: 'YouTube', url: 'https://youtube.com/alexcreates', verified: true }
    ]
  };

  useEffect(() => {
    if (id) {
      setTimeout(() => {
        setProfile(mockProfile);
        setLoading(false);
      }, 500);
    }
  }, [id]);

  const tabs = [
    { id: 'about', label: 'About' },
    { id: 'portfolio', label: 'Portfolio' },
    { id: 'links', label: 'Links' },
    { id: 'metrics', label: 'Metrics' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-neutral-50)] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary-600)]" />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{profile?.name} - Creator Community Platform</title>
        <meta name="description" content={profile?.bio} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-[var(--color-neutral-50)]">
        {/* Header */}
        <header className="bg-white border-b border-[var(--color-neutral-200)]">
          <div className="max-w-7xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-4)]">
            <Button
              variant="ghost"
              onClick={() => router.back()}
              className="mb-[var(--spacing-4)]"
            >
              ← Back
            </Button>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-8)]">
          <div className="flex flex-col lg:flex-row gap-[var(--spacing-8)]">
            {/* Profile Sidebar */}
            <aside className="lg:w-80 flex-shrink-0">
              <Card padding="lg" className="sticky top-[var(--spacing-8)]">
                <div className="text-center mb-[var(--spacing-6)]">
                  <div className="relative inline-block mb-[var(--spacing-4)]">
                    <Avatar 
                      src={profile.avatar} 
                      alt={profile.name}
                      size="2xl"
                    />
                    {profile.isOnline && (
                      <div className="absolute -bottom-1 -right-1 h-6 w-6 bg-[var(--color-accent-500)] border-4 border-white rounded-[var(--radius-full)]" />
                    )}
                  </div>
                  
                  <h1 className="text-[var(--font-size-2xl)] font-bold text-[var(--color-neutral-900)] mb-[var(--spacing-1)]">
                    {profile.name}
                  </h1>
                  <p className="text-[var(--font-size-base)] text-[var(--color-neutral-600)] mb-[var(--spacing-2)]">
                    @{profile.username}
                  </p>
                  
                  <div className="flex items-center justify-center space-x-[var(--spacing-1)] mb-[var(--spacing-4)]">
                    <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)]">
                      {profile.rating}
                    </span>
                    <span className="text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                      ({profile.reviewCount} reviews)
                    </span>
                  </div>
                </div>

                <div className="space-y-[var(--spacing-4)] mb-[var(--spacing-6)]">
                  <div className="flex items-center text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    {profile.location}
                  </div>
                  
                  <div className="flex items-center text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                    </svg>
                    {profile.languages.join(', ')}
                  </div>
                </div>

                <div className="space-y-[var(--spacing-3)]">
                  <Button
                    variant="gradient"
                    size="lg"
                    className="w-full"
                    onClick={() => router.push(`/chat/new?user=${profile.id}`)}
                  >
                    Send Invite
                  </Button>
                  <Button
                    variant="secondary"
                    size="lg"
                    className="w-full"
                    onClick={() => router.push(`/chat/new?user=${profile.id}`)}
                  >
                    Message
                  </Button>
                </div>
              </Card>
            </aside>

            {/* Main Content */}
            <main className="flex-1">
              {/* Tabs */}
              <div className="mb-[var(--spacing-8)]">
                <nav className="flex space-x-[var(--spacing-8)] border-b border-[var(--color-neutral-200)]">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={clsx(
                        'pb-[var(--spacing-4)] text-[var(--font-size-base)] font-medium transition-colors duration-[var(--duration-fast)] border-b-2',
                        activeTab === tab.id
                          ? 'text-[var(--color-primary-600)] border-[var(--color-primary-600)]'
                          : 'text-[var(--color-neutral-500)] border-transparent hover:text-[var(--color-neutral-700)]'
                      )}
                    >
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>

              {/* Tab Content */}
              <div>
                {activeTab === 'about' && (
                  <Card padding="lg">
                    <h2 className="text-[var(--font-size-xl)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-4)]">
                      About
                    </h2>
                    <p className="text-[var(--font-size-base)] text-[var(--color-neutral-700)] leading-relaxed mb-[var(--spacing-6)]">
                      {profile.bio}
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--spacing-6)]">
                      <div>
                        <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-3)]">
                          Skills
                        </h3>
                        <div className="flex flex-wrap gap-[var(--spacing-2)]">
                          {profile.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-[var(--spacing-3)] py-[var(--spacing-2)] rounded-[var(--radius-base)] text-[var(--font-size-sm)] font-medium bg-[var(--color-primary-100)] text-[var(--color-primary-700)]"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-3)]">
                          Categories
                        </h3>
                        <div className="flex flex-wrap gap-[var(--spacing-2)]">
                          {profile.categories.map((category, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-[var(--spacing-3)] py-[var(--spacing-2)] rounded-[var(--radius-base)] text-[var(--font-size-sm)] font-medium bg-[var(--color-secondary-100)] text-[var(--color-secondary-700)]"
                            >
                              {category}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </Card>
                )}

                {activeTab === 'portfolio' && (
                  <Card padding="lg">
                    <h2 className="text-[var(--font-size-xl)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-6)]">
                      Portfolio
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[var(--spacing-6)]">
                      {profile.portfolioItems.map((item) => (
                        <Card key={item.id} hover={true} padding="none" className="overflow-hidden">
                          <div className="aspect-square bg-[var(--color-neutral-200)] flex items-center justify-center">
                            {item.type === 'image' && (
                              <svg className="w-12 h-12 text-[var(--color-neutral-400)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            )}
                            {item.type === 'video' && (
                              <svg className="w-12 h-12 text-[var(--color-neutral-400)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                              </svg>
                            )}
                          </div>
                          <div className="p-[var(--spacing-4)]">
                            <h3 className="text-[var(--font-size-base)] font-medium text-[var(--color-neutral-900)]">
                              {item.title}
                            </h3>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </Card>
                )}

                {activeTab === 'links' && (
                  <Card padding="lg">
                    <h2 className="text-[var(--font-size-xl)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-6)]">
                      Connected Platforms
                    </h2>
                    <div className="space-y-[var(--spacing-4)]">
                      {profile.links.map((link, index) => (
                        <div key={index} className="flex items-center justify-between p-[var(--spacing-4)] bg-[var(--color-neutral-50)] rounded-[var(--radius-lg)]">
                          <div className="flex items-center space-x-[var(--spacing-3)]">
                            <div className="w-10 h-10 bg-[var(--color-primary-100)] rounded-[var(--radius-base)] flex items-center justify-center">
                              <span className="text-[var(--font-size-sm)] font-semibold text-[var(--color-primary-700)]">
                                {link.platform.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <p className="text-[var(--font-size-base)] font-medium text-[var(--color-neutral-900)]">
                                {link.platform}
                              </p>
                              <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                                {link.url}
                              </p>
                            </div>
                          </div>
                          {link.verified && (
                            <span className="inline-flex items-center px-[var(--spacing-2)] py-[var(--spacing-1)] rounded-[var(--radius-sm)] text-[var(--font-size-xs)] font-medium bg-[var(--color-accent-100)] text-[var(--color-accent-700)]">
                              ✓ Verified
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {activeTab === 'metrics' && (
                  <Card padding="lg">
                    <h2 className="text-[var(--font-size-xl)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-6)]">
                      Profile Metrics
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-[var(--spacing-6)]">
                      <div className="text-center">
                        <div className="text-[var(--font-size-3xl)] font-bold text-[var(--color-primary-600)] mb-[var(--spacing-2)]">
                          127
                        </div>
                        <p className="text-[var(--font-size-base)] text-[var(--color-neutral-600)]">
                          Total Reviews
                        </p>
                      </div>
                      <div className="text-center">
                        <div className="text-[var(--font-size-3xl)] font-bold text-[var(--color-secondary-600)] mb-[var(--spacing-2)]">
                          23
                        </div>
                        <p className="text-[var(--font-size-base)] text-[var(--color-neutral-600)]">
                          Collaborations
                        </p>
                      </div>
                      <div className="text-center">
                        <div className="text-[var(--font-size-3xl)] font-bold text-[var(--color-accent-600)] mb-[var(--spacing-2)]">
                          89%
                        </div>
                        <p className="text-[var(--font-size-base)] text-[var(--color-neutral-600)]">
                          Response Rate
                        </p>
                      </div>
                    </div>
                  </Card>
                )}
              </div>
            </main>
          </div>
        </div>
      </div>
    </>
  );
}
