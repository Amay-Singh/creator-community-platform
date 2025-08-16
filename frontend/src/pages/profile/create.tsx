import { useState } from 'react'
import { useRouter } from 'next/router'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { toast } from 'react-hot-toast'
import { profileAPI } from '@/services/api'

interface ProfileForm {
  display_name: string
  bio: string
  category: string
  experience_level: string
  location: string
  website: string
  instagram: string
  tiktok: string
  youtube: string
  skills: string[]
  interests: string[]
}

const CATEGORIES = [
  { value: 'music', label: '🎵 Music', emoji: '🎵' },
  { value: 'visual_art', label: '🎨 Visual Art', emoji: '🎨' },
  { value: 'dance', label: '💃 Dance', emoji: '💃' },
  { value: 'writing', label: '✍️ Writing', emoji: '✍️' },
  { value: 'photography', label: '📸 Photography', emoji: '📸' },
  { value: 'video', label: '🎬 Video/Film', emoji: '🎬' },
  { value: 'fashion', label: '👗 Fashion', emoji: '👗' },
  { value: 'comedy', label: '😂 Comedy', emoji: '😂' },
]

const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: '🌱 Just Starting', desc: 'New to the creative world' },
  { value: 'intermediate', label: '🚀 Getting There', desc: 'Some experience under my belt' },
  { value: 'advanced', label: '⭐ Pretty Good', desc: 'Confident in my skills' },
  { value: 'expert', label: '🏆 Pro Level', desc: 'Ready to mentor others' },
]

const SKILL_OPTIONS = [
  'Songwriting', 'Music Production', 'Singing', 'Guitar', 'Piano', 'Photography',
  'Video Editing', 'Graphic Design', 'Dancing', 'Acting', 'Writing', 'Social Media',
  'Marketing', 'Branding', 'Animation', 'Web Design', 'Fashion Design', 'Makeup',
]

export default function CreateProfilePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])

  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<ProfileForm>()

  const onSubmit = async (data: ProfileForm) => {
    setIsLoading(true)
    try {
      const profileData = {
        ...data,
        skills: selectedSkills,
        interests: selectedInterests,
      }
      
      await profileAPI.createProfile(profileData)
      toast.success('Profile created! Welcome to the creator community! 🎉')
      router.push('/dashboard')
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Profile creation failed')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleSkill = (skill: string) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill))
    } else if (selectedSkills.length < 8) {
      setSelectedSkills([...selectedSkills, skill])
    } else {
      toast.error('Maximum 8 skills allowed')
    }
  }

  const toggleInterest = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter(i => i !== interest))
    } else if (selectedInterests.length < 10) {
      setSelectedInterests([...selectedInterests, interest])
    } else {
      toast.error('Maximum 10 interests allowed')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      {/* Progress indicator */}
      <div className="max-w-2xl mx-auto pt-8 pb-4">
        <div className="flex items-center justify-between mb-8">
          {[1, 2, 3].map((stepNum) => (
            <div key={stepNum} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  step >= stepNum
                    ? 'bg-gradient-to-r from-yellow-400 to-pink-500 text-white'
                    : 'bg-white/20 text-purple-200'
                }`}
              >
                {step > stepNum ? '✓' : stepNum}
              </div>
              {stepNum < 3 && (
                <div
                  className={`w-20 h-1 mx-2 transition-all ${
                    step > stepNum ? 'bg-gradient-to-r from-yellow-400 to-pink-500' : 'bg-white/20'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl mx-auto"
      >
        <Card className="backdrop-blur-lg bg-white/10 border-white/20">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold text-white mb-2">
              {step === 1 && "Let's Get to Know You! 🌟"}
              {step === 2 && "What's Your Vibe? 🎨"}
              {step === 3 && "Connect Your World 🌐"}
            </CardTitle>
            <p className="text-purple-200">
              {step === 1 && "Tell us about yourself and your creative journey"}
              {step === 2 && "Choose your category and experience level"}
              {step === 3 && "Add your skills and social links"}
            </p>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {step === 1 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  <Input
                    placeholder="Your display name ✨"
                    {...register('display_name', { required: 'Display name is required' })}
                    error={errors.display_name?.message}
                    className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                  />

                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-2">
                      Tell us about yourself 📝
                    </label>
                    <textarea
                      placeholder="I'm a passionate creator who loves..."
                      {...register('bio', { required: 'Bio is required' })}
                      className="w-full h-32 rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-purple-200 resize-none focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                    />
                    {errors.bio && (
                      <p className="text-red-400 text-sm mt-1">⚠️ {errors.bio.message}</p>
                    )}
                  </div>

                  <Input
                    placeholder="Your location 📍"
                    {...register('location')}
                    className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                  />
                </motion.div>
              )}

              {step === 2 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-4">
                      What's your main creative category? 🎭
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      {CATEGORIES.map((cat) => (
                        <button
                          key={cat.value}
                          type="button"
                          onClick={() => setValue('category', cat.value)}
                          className={`p-4 rounded-xl border-2 transition-all text-left ${
                            watch('category') === cat.value
                              ? 'border-yellow-400 bg-yellow-400/20 text-white'
                              : 'border-white/20 bg-white/5 text-purple-200 hover:border-purple-400'
                          }`}
                        >
                          <div className="text-2xl mb-1">{cat.emoji}</div>
                          <div className="font-medium">{cat.label.replace(cat.emoji + ' ', '')}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-4">
                      What's your experience level? 🎯
                    </label>
                    <div className="space-y-3">
                      {EXPERIENCE_LEVELS.map((level) => (
                        <button
                          key={level.value}
                          type="button"
                          onClick={() => setValue('experience_level', level.value)}
                          className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                            watch('experience_level') === level.value
                              ? 'border-yellow-400 bg-yellow-400/20 text-white'
                              : 'border-white/20 bg-white/5 text-purple-200 hover:border-purple-400'
                          }`}
                        >
                          <div className="font-medium">{level.label}</div>
                          <div className="text-sm opacity-80">{level.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {step === 3 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-4">
                      Your skills (max 8) 🛠️
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {SKILL_OPTIONS.map((skill) => (
                        <button
                          key={skill}
                          type="button"
                          onClick={() => toggleSkill(skill)}
                          className={`p-2 rounded-lg text-xs transition-all ${
                            selectedSkills.includes(skill)
                              ? 'bg-gradient-to-r from-yellow-400 to-pink-500 text-white'
                              : 'bg-white/10 text-purple-200 hover:bg-white/20'
                          }`}
                        >
                          {skill}
                        </button>
                      ))}
                    </div>
                    <p className="text-purple-300 text-xs mt-2">
                      Selected: {selectedSkills.length}/8
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      placeholder="Website URL 🌐"
                      {...register('website')}
                      className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                    />
                    <Input
                      placeholder="Instagram handle 📸"
                      {...register('instagram')}
                      className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                    />
                    <Input
                      placeholder="TikTok handle 🎵"
                      {...register('tiktok')}
                      className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                    />
                    <Input
                      placeholder="YouTube channel 📺"
                      {...register('youtube')}
                      className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                    />
                  </div>
                </motion.div>
              )}

              <div className="flex justify-between pt-6">
                {step > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setStep(step - 1)}
                    className="border-white/20 text-purple-200 hover:bg-white/10"
                  >
                    ← Back
                  </Button>
                )}
                
                {step < 3 ? (
                  <Button
                    type="button"
                    variant="gradient"
                    onClick={() => setStep(step + 1)}
                    className="ml-auto"
                    disabled={
                      (step === 1 && (!watch('display_name') || !watch('bio'))) ||
                      (step === 2 && (!watch('category') || !watch('experience_level')))
                    }
                  >
                    Next →
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    variant="gradient"
                    size="lg"
                    isLoading={isLoading}
                    className="ml-auto"
                  >
                    Create Profile 🚀
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
