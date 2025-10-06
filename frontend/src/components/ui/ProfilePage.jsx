import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from './Card';
import Button from './Button';

/**
 * Profile Page Component - ReqDoc02 Phase 3
 * Features: Cover image, tabbed content, portfolio lightbox
 */
const ProfilePage = ({ creator, isOwnProfile = false }) => {
  const [activeTab, setActiveTab] = useState('about');
  const [lightboxImage, setLightboxImage] = useState(null);
  const [isFollowing, setIsFollowing] = useState(creator.isFollowing || false);

  const tabs = [
    { id: 'about', label: 'About', icon: 'user' },
    { id: 'portfolio', label: 'Portfolio', icon: 'folder' },
    { id: 'collaborations', label: 'Collaborations', icon: 'users' },
    { id: 'reviews', label: 'Reviews', icon: 'star' }
  ];

  const IconComponent = ({ name, className }) => {
    const icons = {
      user: (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      folder: (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        </svg>
      ),
      users: (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      star: (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      )
    };
    return icons[name] || null;
  };

  const handleFollow = () => {
    setIsFollowing(!isFollowing);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Cover Section */}
      <motion.div 
        className="relative h-80 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 overflow-hidden"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        {creator.coverImage && (
          <img
            src={creator.coverImage}
            alt={`${creator.name}'s cover`}
            className="w-full h-full object-cover"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent"></div>
        
        {/* Profile Info Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-8">
          <div className="max-w-6xl mx-auto flex items-end justify-between">
            <div className="flex items-end space-x-6">
              {/* Avatar */}
              <motion.div 
                className="relative"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <div className="w-32 h-32 rounded-3xl overflow-hidden bg-white p-1 shadow-2xl">
                  <img
                    src={creator.avatar || '/default-avatar.png'}
                    alt={creator.name}
                    className="w-full h-full object-cover rounded-3xl"
                  />
                </div>
                {creator.isOnline && (
                  <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 border-4 border-white rounded-full"></div>
                )}
              </motion.div>

              {/* Basic Info */}
              <motion.div 
                className="text-white mb-4"
                initial={{ x: -30, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <h1 className="text-4xl font-bold mb-2">{creator.name}</h1>
                <p className="text-xl text-blue-100 mb-2">{creator.title}</p>
                <div className="flex items-center space-x-4 text-blue-100">
                  <span className="flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {creator.location}
                  </span>
                  <span className="flex items-center">
                    <svg className="w-5 h-5 mr-2 text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                    {creator.rating} ({creator.reviewCount} reviews)
                  </span>
                </div>
              </motion.div>
            </div>

            {/* Action Buttons */}
            {!isOwnProfile && (
              <motion.div 
                className="flex space-x-4 mb-4"
                initial={{ x: 30, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.7 }}
              >
                <Button variant="glass" onClick={handleFollow}>
                  {isFollowing ? 'Following' : 'Follow'}
                </Button>
                <Button variant="primary">
                  Collaborate
                </Button>
                <Button variant="glass">
                  Message
                </Button>
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-8 -mt-16 relative z-10">
        {/* Stats Cards */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {[
            { label: 'Projects', value: creator.projectCount || 0, color: 'from-blue-500 to-purple-500' },
            { label: 'Followers', value: creator.followerCount || 0, color: 'from-purple-500 to-pink-500' },
            { label: 'Following', value: creator.followingCount || 0, color: 'from-green-500 to-emerald-500' },
            { label: 'Success Rate', value: `${creator.successRate || 0}%`, color: 'from-orange-500 to-red-500' }
          ].map((stat, index) => (
            <Card key={stat.label} variant="glass" className="text-center p-6">
              <div className={`text-3xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent mb-2`}>
                {stat.value}
              </div>
              <div className="text-gray-600 font-medium">{stat.label}</div>
            </Card>
          ))}
        </motion.div>

        {/* Tabbed Content */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Card variant="glass" className="overflow-hidden">
            {/* Tab Navigation */}
            <div className="flex border-b border-white/20">
              {tabs.map((tab, index) => (
                <motion.button
                  key={tab.id}
                  className={`flex items-center space-x-2 px-6 py-4 font-medium transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-white/20'
                  }`}
                  onClick={() => setActiveTab(tab.id)}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <IconComponent name={tab.icon} className="w-5 h-5" />
                  <span>{tab.label}</span>
                </motion.button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="p-8">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {activeTab === 'about' && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-4">About</h3>
                        <p className="text-gray-600 leading-relaxed">{creator.bio}</p>
                      </div>
                      
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-4">Skills & Expertise</h3>
                        <div className="flex flex-wrap gap-3">
                          {(creator.skills || []).map((skill, index) => (
                            <span
                              key={index}
                              className="px-4 py-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-700 rounded-full font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-4">Experience</h3>
                        <p className="text-gray-600">{creator.experience || 'No experience information available.'}</p>
                      </div>
                    </div>
                  )}

                  {activeTab === 'portfolio' && (
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-6">Portfolio</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {(creator.portfolio || []).map((item, index) => (
                          <motion.div
                            key={index}
                            className="relative group cursor-pointer rounded-2xl overflow-hidden"
                            whileHover={{ scale: 1.05 }}
                            onClick={() => setLightboxImage(item)}
                          >
                            <img
                              src={item.image}
                              alt={item.title}
                              className="w-full h-48 object-cover"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                              <div className="absolute bottom-4 left-4 text-white">
                                <h4 className="font-semibold">{item.title}</h4>
                                <p className="text-sm text-gray-200">{item.category}</p>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === 'collaborations' && (
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Collaborations</h3>
                      <div className="space-y-4">
                        {(creator.collaborations || []).map((collab, index) => (
                          <Card key={index} variant="default" className="p-6">
                            <div className="flex items-start space-x-4">
                              <img
                                src={collab.image}
                                alt={collab.title}
                                className="w-16 h-16 rounded-2xl object-cover"
                              />
                              <div className="flex-1">
                                <h4 className="font-semibold text-gray-900 mb-1">{collab.title}</h4>
                                <p className="text-gray-600 text-sm mb-2">{collab.description}</p>
                                <div className="flex items-center space-x-4 text-sm text-gray-500">
                                  <span>With {collab.collaborators.join(', ')}</span>
                                  <span>{collab.date}</span>
                                </div>
                              </div>
                            </div>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === 'reviews' && (
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-6">Reviews & Testimonials</h3>
                      <div className="space-y-6">
                        {(creator.reviews || []).map((review, index) => (
                          <Card key={index} variant="default" className="p-6">
                            <div className="flex items-start space-x-4">
                              <img
                                src={review.avatar}
                                alt={review.name}
                                className="w-12 h-12 rounded-full object-cover"
                              />
                              <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                  <h4 className="font-semibold text-gray-900">{review.name}</h4>
                                  <div className="flex items-center">
                                    {[...Array(5)].map((_, i) => (
                                      <svg
                                        key={i}
                                        className={`w-4 h-4 ${i < review.rating ? 'text-yellow-500' : 'text-gray-300'}`}
                                        fill="currentColor"
                                        viewBox="0 0 24 24"
                                      >
                                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                                      </svg>
                                    ))}
                                  </div>
                                </div>
                                <p className="text-gray-600 mb-2">{review.comment}</p>
                                <p className="text-sm text-gray-500">{review.date}</p>
                              </div>
                            </div>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Portfolio Lightbox */}
      <AnimatePresence>
        {lightboxImage && (
          <motion.div
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setLightboxImage(null)}
          >
            <motion.div
              className="relative max-w-4xl max-h-full"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={lightboxImage.image}
                alt={lightboxImage.title}
                className="max-w-full max-h-full object-contain rounded-2xl"
              />
              <button
                className="absolute top-4 right-4 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors"
                onClick={() => setLightboxImage(null)}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <div className="absolute bottom-4 left-4 text-white">
                <h3 className="text-xl font-bold mb-1">{lightboxImage.title}</h3>
                <p className="text-gray-200">{lightboxImage.description}</p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProfilePage;
