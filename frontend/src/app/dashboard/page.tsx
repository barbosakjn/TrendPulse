'use client';

import { useEffect, useState, useCallback } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import Header from '@/components/layout/Header';
import { useAuthStore } from '@/stores/authStore';
import { initializeAuth } from '@/lib/auth';
import { 
  TrendingUp, 
  BarChart3, 
  Search,
  Zap,
  Globe,
  Youtube,
  MessageSquare,
  ChevronRight,
  Target,
  Flame,
  Loader2,
  ExternalLink,
  RefreshCw,
  X,
  Sparkles,
  AlertCircle
} from 'lucide-react';

interface GoogleTrend {
  rank: number;
  query: string;
  title: string;
}

interface KeywordInterest {
  date: string;
  value: number;
}

interface YouTubeVideo {
  video_id: string;
  title: string;
  channel: { title: string };
  statistics: { view_count: number };
  url: string;
}

interface RedditPost {
  post_id: string;
  title: string;
  subreddit: string;
  upvotes: number;
  num_comments: number;
  url: string;
}

interface ExaResult {
  id: string;
  title: string;
  url: string;
  score: number;
  text?: string;
}

interface TwitterTweet {
  tweet_id: string;
  text: string;
  user: { name: string; screen_name: string; followers_count: number };
  retweet_count: number;
  favorite_count: number;
  url: string;
}

type DataSource = 'google' | 'youtube' | 'reddit' | 'exa' | 'twitter';

interface LoadingState {
  google: boolean;
  youtube: boolean;
  reddit: boolean;
  exa: boolean;
  twitter: boolean;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [greeting, setGreeting] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeSource, setActiveSource] = useState<DataSource>('exa');
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchedKeyword, setSearchedKeyword] = useState('');

  const [loading, setLoading] = useState<LoadingState>({
    google: false,
    youtube: false,
    reddit: false,
    exa: false,
    twitter: false
  });
  const [errors, setErrors] = useState<Record<DataSource, string | null>>({
    google: null,
    youtube: null,
    reddit: null,
    exa: null,
    twitter: null
  });

  const [googleTrends, setGoogleTrends] = useState<GoogleTrend[]>([]);
  const [keywordData, setKeywordData] = useState<KeywordInterest[]>([]);
  const [youtubeVideos, setYoutubeVideos] = useState<YouTubeVideo[]>([]);
  const [redditPosts, setRedditPosts] = useState<RedditPost[]>([]);
  const [exaResults, setExaResults] = useState<ExaResult[]>([]);
  const [twitterTweets, setTwitterTweets] = useState<TwitterTweet[]>([]);

  const [stats, setStats] = useState({
    totalTrends: 0,
    trendingNow: 0,
    lastUpdated: ''
  });

  useEffect(() => {
    initializeAuth();
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 18) setGreeting('Good afternoon');
    else setGreeting('Good evening');

    fetchTrendingData();
  }, []);

  const setSourceLoading = (source: DataSource, isLoading: boolean) => {
    setLoading(prev => ({ ...prev, [source]: isLoading }));
  };

  const setSourceError = (source: DataSource, error: string | null) => {
    setErrors(prev => ({ ...prev, [source]: error }));
  };

  const fetchTrendingData = async () => {
    setSourceLoading('google', true);
    setSourceError('google', null);

    try {
      const response = await fetch('/api/trends/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'trending_searches', country: 'united_states' })
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.trends) {
        setGoogleTrends(data.trends.slice(0, 10));
        setStats({
          totalTrends: data.count || data.trends.length,
          trendingNow: Math.min(5, data.trends.length),
          lastUpdated: new Date().toLocaleTimeString()
        });
      } else {
        setSourceError('google', data.message || 'Google Trends is temporarily unavailable. Try again later.');
      }
    } catch (err) {
      setSourceError('google', 'Failed to connect to Google Trends. Check your connection.');
    } finally {
      setSourceLoading('google', false);
    }
  };

  const searchGoogle = async (keyword: string) => {
    setSourceLoading('google', true);
    setSourceError('google', null);
    setSearchedKeyword(keyword);

    try {
      const response = await fetch('/api/trends/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'keyword_interest', 
          keyword, 
          timeframe: 'today 12-m', 
          geo: 'US' 
        })
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.data) {
        setKeywordData(data.data);
      } else {
        setSourceError('google', data.message || 'Could not fetch keyword data.');
      }
    } catch (err) {
      setSourceError('google', 'Failed to search Google Trends.');
    } finally {
      setSourceLoading('google', false);
    }
  };

  const searchYouTube = async (query?: string) => {
    setSourceLoading('youtube', true);
    setSourceError('youtube', null);

    try {
      const requestBody = query 
        ? { action: 'search', query, country: 'US', max_results: 10 }
        : { action: 'trending_videos', country: 'US', max_results: 10 };

      const response = await fetch('/api/trends/youtube', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.videos) {
        setYoutubeVideos(data.videos);
        if (query) setSearchedKeyword(query);
      } else {
        setSourceError('youtube', data.message || 'YouTube API requires an API key. Configure GOOGLE_API_KEY in secrets.');
      }
    } catch (err) {
      setSourceError('youtube', 'Failed to fetch YouTube trends.');
    } finally {
      setSourceLoading('youtube', false);
    }
  };

  const searchReddit = async (subreddit: string) => {
    setSourceLoading('reddit', true);
    setSourceError('reddit', null);

    try {
      const response = await fetch('/api/trends/reddit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subreddit: subreddit || 'all', limit: 10 })
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.posts) {
        setRedditPosts(data.posts);
      } else {
        setSourceError('reddit', data.message || 'Reddit access is limited. Some content may not be available.');
      }
    } catch (err) {
      setSourceError('reddit', 'Failed to fetch Reddit posts.');
    } finally {
      setSourceLoading('reddit', false);
    }
  };

  const searchExa = async (query: string) => {
    setSourceLoading('exa', true);
    setSourceError('exa', null);

    try {
      const response = await fetch('/api/trends/exa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'search_trending', 
          query, 
          num_results: 10 
        })
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.results) {
        setExaResults(data.results);
      } else {
        setSourceError('exa', data.message || 'EXA AI requires an API key. Configure EXA_API_KEY in secrets.');
      }
    } catch (err) {
      setSourceError('exa', 'Failed to search with EXA AI.');
    } finally {
      setSourceLoading('exa', false);
    }
  };

  const searchTwitter = async (query: string) => {
    setSourceLoading('twitter', true);
    setSourceError('twitter', null);

    try {
      const response = await fetch('/api/trends/twitter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'search', 
          query, 
          max_results: 10 
        })
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.tweets) {
        setTwitterTweets(data.tweets);
        setSearchedKeyword(query);
      } else {
        setSourceError('twitter', data.message || 'Twitter/X requires login. Configure TWITTER_USERNAME, TWITTER_EMAIL, and TWITTER_PASSWORD.');
      }
    } catch (err) {
      setSourceError('twitter', 'Failed to search Twitter/X.');
    } finally {
      setSourceLoading('twitter', false);
    }
  };

  const handleSearch = useCallback(() => {
    if (!searchQuery.trim()) return;
    
    setShowSearchModal(false);
    
    switch (activeSource) {
      case 'google':
        searchGoogle(searchQuery);
        break;
      case 'youtube':
        searchYouTube(searchQuery);
        break;
      case 'reddit':
        searchReddit(searchQuery);
        break;
      case 'exa':
        searchExa(searchQuery);
        break;
      case 'twitter':
        searchTwitter(searchQuery);
        break;
    }
  }, [searchQuery, activeSource]);

  const handleQuickAction = (source: DataSource, defaultQuery?: string) => {
    setActiveSource(source);
    if (defaultQuery) {
      setSearchQuery(defaultQuery);
      switch (source) {
        case 'youtube':
          searchYouTube(defaultQuery);
          break;
        case 'reddit':
          searchReddit(defaultQuery);
          break;
        case 'exa':
          searchExa(defaultQuery);
          break;
        case 'google':
          searchGoogle(defaultQuery);
          break;
        case 'twitter':
          searchTwitter(defaultQuery);
          break;
      }
    } else {
      setShowSearchModal(true);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const isAnyLoading = Object.values(loading).some(Boolean);
  const hasResults = youtubeVideos.length > 0 || redditPosts.length > 0 || exaResults.length > 0 || keywordData.length > 0;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
        <Header />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-10">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-indigo-400 font-medium text-sm uppercase tracking-wider">Dashboard</span>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent mb-3">
              {greeting}, {user?.name?.split(' ')[0] || 'there'}!
            </h1>
            <p className="text-slate-400 text-lg">
              Discover what's trending in your niche today
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div className="group relative overflow-hidden bg-gradient-to-br from-indigo-600/20 to-indigo-900/20 backdrop-blur-xl rounded-2xl border border-indigo-500/20 p-6 hover:border-indigo-500/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-indigo-500/20 rounded-xl">
                    <TrendingUp className="w-6 h-6 text-indigo-400" />
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">
                  {loading.google ? '...' : stats.totalTrends || googleTrends.length}
                </span>
                <h3 className="text-sm font-medium text-slate-400">Active Trends</h3>
              </div>
            </div>

            <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-600/20 to-emerald-900/20 backdrop-blur-xl rounded-2xl border border-emerald-500/20 p-6 hover:border-emerald-500/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-emerald-500/20 rounded-xl">
                    <Target className="w-6 h-6 text-emerald-400" />
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">
                  {youtubeVideos.length + redditPosts.length}
                </span>
                <h3 className="text-sm font-medium text-slate-400">Content Found</h3>
              </div>
            </div>

            <div className="group relative overflow-hidden bg-gradient-to-br from-purple-600/20 to-purple-900/20 backdrop-blur-xl rounded-2xl border border-purple-500/20 p-6 hover:border-purple-500/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-purple-500/20 rounded-xl">
                    <BarChart3 className="w-6 h-6 text-purple-400" />
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">{exaResults.length}</span>
                <h3 className="text-sm font-medium text-slate-400">AI Insights</h3>
              </div>
            </div>

            <div className="group relative overflow-hidden bg-gradient-to-br from-orange-600/20 to-orange-900/20 backdrop-blur-xl rounded-2xl border border-orange-500/20 p-6 hover:border-orange-500/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-orange-500/20 rounded-xl">
                    <Flame className="w-6 h-6 text-orange-400" />
                  </div>
                  <div className="flex items-center gap-1 text-orange-400 text-sm font-medium bg-orange-500/10 px-2 py-1 rounded-full">
                    <Zap className="w-3 h-3" />
                    <span>Live</span>
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">{stats.trendingNow}</span>
                <h3 className="text-sm font-medium text-slate-400">Hot Topics</h3>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2 bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Top Trending Topics</h2>
                  <p className="text-slate-500 text-sm">
                    {stats.lastUpdated ? `Updated ${stats.lastUpdated}` : 'Live from Google Trends'}
                  </p>
                </div>
                <button 
                  onClick={fetchTrendingData}
                  disabled={loading.google}
                  className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${loading.google ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
              
              {loading.google && googleTrends.length === 0 ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                </div>
              ) : errors.google ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <AlertCircle className="w-12 h-12 text-amber-500 mb-4" />
                  <p className="text-slate-400 mb-2">{errors.google}</p>
                  <button 
                    onClick={fetchTrendingData}
                    className="text-indigo-400 hover:text-indigo-300 text-sm"
                  >
                    Try again
                  </button>
                </div>
              ) : googleTrends.length > 0 ? (
                <div className="space-y-3">
                  {googleTrends.slice(0, 10).map((trend, index) => (
                    <div 
                      key={trend.rank}
                      className="group flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all cursor-pointer border border-transparent hover:border-slate-700/50"
                    >
                      <div className={`flex items-center justify-center w-10 h-10 rounded-xl ${
                        index === 0 ? 'bg-gradient-to-br from-yellow-500 to-orange-500' :
                        index === 1 ? 'bg-gradient-to-br from-slate-400 to-slate-500' :
                        index === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700' :
                        'bg-gradient-to-br from-indigo-500 to-purple-500'
                      }`}>
                        <span className="text-white font-bold text-sm">#{trend.rank}</span>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-white group-hover:text-indigo-300 transition-colors">
                          {trend.title || trend.query}
                        </h3>
                        <p className="text-sm text-slate-400">Trending on Google</p>
                      </div>
                      <button 
                        onClick={() => handleQuickAction('exa', trend.query)}
                        className="p-2 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 transition-colors"
                        title="Research this topic"
                      >
                        <Search className="w-4 h-4 text-indigo-400" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <Globe className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No trends loaded yet. Click Refresh to fetch latest data.</p>
                </div>
              )}
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Quick Actions</h2>
              </div>
              
              <div className="space-y-3">
                <button 
                  onClick={() => setShowSearchModal(true)}
                  disabled={isAnyLoading}
                  className="w-full flex items-center gap-3 p-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-xl transition-all group disabled:opacity-50"
                >
                  <Search className="w-5 h-5 text-white" />
                  <span className="font-medium text-white">Search Trends</span>
                  <ChevronRight className="w-4 h-4 text-white/70 ml-auto group-hover:translate-x-1 transition-transform" />
                </button>
                
                <button 
                  onClick={() => handleQuickAction('google')}
                  disabled={loading.google}
                  className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group disabled:opacity-50"
                >
                  {loading.google ? (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                  ) : (
                    <Globe className="w-5 h-5 text-blue-400" />
                  )}
                  <span className="font-medium text-slate-300">Google Trends</span>
                  <ChevronRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-1 transition-transform" />
                </button>

                <button 
                  onClick={() => handleQuickAction('youtube')}
                  disabled={loading.youtube}
                  className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group disabled:opacity-50"
                >
                  {loading.youtube ? (
                    <Loader2 className="w-5 h-5 text-red-400 animate-spin" />
                  ) : (
                    <Youtube className="w-5 h-5 text-red-400" />
                  )}
                  <span className="font-medium text-slate-300">YouTube</span>
                  <ChevronRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-1 transition-transform" />
                </button>

                <button 
                  onClick={() => handleQuickAction('twitter')}
                  disabled={loading.twitter}
                  className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group disabled:opacity-50"
                >
                  {loading.twitter ? (
                    <Loader2 className="w-5 h-5 text-slate-200 animate-spin" />
                  ) : (
                    <svg className="w-5 h-5 text-slate-200" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                  )}
                  <span className="font-medium text-slate-300">X/Twitter</span>
                  <ChevronRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-1 transition-transform" />
                </button>
                
                <button 
                  onClick={() => handleQuickAction('reddit')}
                  disabled={loading.reddit}
                  className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group disabled:opacity-50"
                >
                  {loading.reddit ? (
                    <Loader2 className="w-5 h-5 text-orange-400 animate-spin" />
                  ) : (
                    <MessageSquare className="w-5 h-5 text-orange-400" />
                  )}
                  <span className="font-medium text-slate-300">Reddit</span>
                  <ChevronRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-1 transition-transform" />
                </button>

                <button 
                  onClick={() => handleQuickAction('exa')}
                  disabled={loading.exa}
                  className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group disabled:opacity-50"
                >
                  {loading.exa ? (
                    <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                  ) : (
                    <Zap className="w-5 h-5 text-purple-400" />
                  )}
                  <span className="font-medium text-slate-300">AI Research</span>
                  <ChevronRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          </div>

          {hasResults && (
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Search Results</h2>
                  <p className="text-slate-500 text-sm">
                    {searchedKeyword && `Results for "${searchedKeyword}"`}
                    {youtubeVideos.length > 0 && ` • ${youtubeVideos.length} videos`}
                    {redditPosts.length > 0 && ` • ${redditPosts.length} posts`}
                    {exaResults.length > 0 && ` • ${exaResults.length} insights`}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setYoutubeVideos([]);
                    setRedditPosts([]);
                    setExaResults([]);
                    setKeywordData([]);
                    setSearchedKeyword('');
                  }}
                  className="text-slate-400 hover:text-white text-sm"
                >
                  Clear
                </button>
              </div>

              <div className="space-y-3">
                {youtubeVideos.slice(0, 5).map((video) => (
                  <a 
                    key={video.video_id}
                    href={video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all border border-transparent hover:border-red-500/30"
                  >
                    <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl">
                      <Youtube className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white truncate">{video.title}</h3>
                      <p className="text-sm text-slate-400">
                        {video.channel.title} • {formatNumber(video.statistics.view_count)} views
                      </p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  </a>
                ))}

                {redditPosts.slice(0, 5).map((post) => (
                  <a 
                    key={post.post_id}
                    href={post.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all border border-transparent hover:border-orange-500/30"
                  >
                    <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl">
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white truncate">{post.title}</h3>
                      <p className="text-sm text-slate-400">
                        r/{post.subreddit} • {formatNumber(post.upvotes)} upvotes • {post.num_comments} comments
                      </p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  </a>
                ))}

                {exaResults.slice(0, 5).map((result) => (
                  <a 
                    key={result.id}
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all border border-transparent hover:border-purple-500/30"
                  >
                    <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl">
                      <Zap className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white truncate">{result.title}</h3>
                      {result.text && (
                        <p className="text-sm text-slate-400 truncate">{result.text}</p>
                      )}
                    </div>
                    <ExternalLink className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  </a>
                ))}
              </div>

              {(errors.youtube || errors.reddit || errors.exa || errors.twitter) && (
                <div className="mt-4 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-amber-300">
                      {errors.youtube && <p>{errors.youtube}</p>}
                      {errors.twitter && <p>{errors.twitter}</p>}
                      {errors.reddit && <p>{errors.reddit}</p>}
                      {errors.exa && <p>{errors.exa}</p>}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Data Sources</h2>
                <p className="text-slate-500 text-sm">Connected platforms for trend discovery</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="p-4 bg-slate-800/30 rounded-xl text-center">
                <Globe className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                <p className="text-white font-medium">Google Trends</p>
                <p className={`text-xs ${errors.google ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {errors.google ? 'Limited' : 'Connected'}
                </p>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-xl text-center">
                <Youtube className="w-8 h-8 text-red-400 mx-auto mb-2" />
                <p className="text-white font-medium">YouTube</p>
                <p className={`text-xs ${errors.youtube ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {errors.youtube ? 'Needs API Key' : 'Connected'}
                </p>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-xl text-center">
                <svg className="w-8 h-8 text-slate-200 mx-auto mb-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
                <p className="text-white font-medium">X/Twitter</p>
                <p className={`text-xs ${errors.twitter ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {errors.twitter ? 'Needs Login' : 'Connected'}
                </p>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-xl text-center">
                <MessageSquare className="w-8 h-8 text-orange-400 mx-auto mb-2" />
                <p className="text-white font-medium">Reddit</p>
                <p className="text-xs text-slate-400">Read-only</p>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-xl text-center">
                <Zap className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-white font-medium">Exa AI</p>
                <p className={`text-xs ${errors.exa ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {errors.exa ? 'Needs API Key' : 'Connected'}
                </p>
              </div>
            </div>
          </div>
        </main>

        {showSearchModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">Search Trends</h3>
                <button 
                  onClick={() => setShowSearchModal(false)}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>

              <div className="flex gap-2 mb-4 flex-wrap">
                {(['exa', 'google', 'youtube', 'twitter', 'reddit'] as DataSource[]).map((source) => (
                  <button
                    key={source}
                    onClick={() => setActiveSource(source)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeSource === source 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {source === 'exa' ? 'AI Search' : source === 'twitter' ? 'X/Twitter' : source.charAt(0).toUpperCase() + source.slice(1)}
                  </button>
                ))}
              </div>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder={
                    activeSource === 'reddit' 
                      ? 'Enter subreddit name (e.g., technology)' 
                      : activeSource === 'google'
                      ? 'Enter keyword to analyze'
                      : activeSource === 'youtube'
                      ? 'Search YouTube videos (e.g., AI trends)'
                      : activeSource === 'twitter'
                      ? 'Search tweets (e.g., AI trends)'
                      : 'What trends are you looking for?'
                  }
                  className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={isAnyLoading || !searchQuery.trim()}
                  className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-medium transition-colors flex items-center gap-2"
                >
                  {isAnyLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5" />
                  )}
                </button>
              </div>

              <p className="text-sm text-slate-500">
                {activeSource === 'google' && 'Analyze keyword interest over time on Google Trends'}
                {activeSource === 'youtube' && 'Search YouTube videos by keyword'}
                {activeSource === 'twitter' && 'Search tweets by keyword on X/Twitter'}
                {activeSource === 'reddit' && 'Get hot posts from any subreddit'}
                {activeSource === 'exa' && 'AI-powered web search for trends and insights'}
              </p>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
