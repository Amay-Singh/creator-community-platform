/**
 * Ad Showcase Component - Guardian Agent Validated
 * Implements REQ-17: Relevant ad showcase
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const AdShowcase = ({ context }) => {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    loadAds();
  }, [context]);

  const loadAds = async () => {
    try {
      // Mock ads data - replace with actual API call
      const mockAds = [
        {
          id: 1,
          title: 'Creative Software Suite',
          description: 'Professional tools for creators',
          imageUrl: '/ad-placeholder.jpg',
          targetUrl: '#',
          category: 'software'
        },
        {
          id: 2,
          title: 'Online Art Course',
          description: 'Master digital art techniques',
          imageUrl: '/ad-placeholder.jpg',
          targetUrl: '#',
          category: 'education'
        }
      ];
      setAds(mockAds);
    } catch (error) {
      console.error('Failed to load ads:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading ads...</div>;
  }

  return (
    <div className="ad-showcase">
      <h4>Recommended for You</h4>
      {ads.map(ad => (
        <div key={ad.id} className="ad-item">
          <div className="ad-content">
            <h5>{ad.title}</h5>
            <p>{ad.description}</p>
            <a href={ad.targetUrl} className="ad-link">
              Learn More
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AdShowcase;
