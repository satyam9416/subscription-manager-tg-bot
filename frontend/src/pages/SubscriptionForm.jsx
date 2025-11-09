import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProduct, createSubscription } from '../services/api'

function SubscriptionForm() {
  const { productId } = useParams()
  const navigate = useNavigate()
  
  const [product, setProduct] = useState(null)
  const [email, setEmail] = useState('')
  const [expirationDate, setExpirationDate] = useState('')
  const [forceRenew, setForceRenew] = useState(false);
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [subscriptionData, setSubscriptionData] = useState(null)

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await getProduct(productId)
        setProduct(response.data)
        setLoading(false)
      } catch (err) {
        setError('Failed to load product information. Please try again later.')
        setLoading(false)
      }
    }

    fetchProduct()
  }, [productId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    
    try {
      const subscriptionData = { 
        email, 
        product_id: parseInt(productId)
      }
      
      // Add expiration date if provided
      if (expirationDate) {
        subscriptionData.expiration_datetime = new Date(expirationDate).toISOString()
      }
      
      const response = await createSubscription(subscriptionData, forceRenew);
      setSuccess('Subscription created successfully!')
      setSubscriptionData(response.data)
      setSubmitting(false)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create subscription. Please try again.')
      setSubmitting(false)
    }
  }

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading product information...</div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Product not found.
      </div>
    )
  }

  // Check if product has a mapped Telegram group
  const hasTelegramGroup = !!product.telegram_group;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Subscribe to {product.name}
      </h1>

      {!hasTelegramGroup && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg mb-6 flex items-start">
          <svg
            className="h-6 w-6 text-yellow-400 mr-3 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <p className="text-yellow-700">
            This product is not currently mapped to a Telegram group. You can
            still subscribe, but you won't receive an invite link.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg mb-6 flex items-start">
          <svg
            className="h-6 w-6 text-red-400 mr-3 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {success ? (
        <div className="bg-white shadow-lg rounded-lg border border-green-200 overflow-hidden">
          <div className="bg-green-50 px-6 py-4 border-b border-green-100">
            <div className="flex items-center">
              <svg
                className="h-6 w-6 text-green-500 mr-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <h3 className="text-lg font-medium text-green-800">{success}</h3>
            </div>
          </div>

          <div className="px-6 py-4">
            {subscriptionData?.invite_link && (
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                  Telegram Invite Link
                </h4>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 break-all">
                  <a
                    href={subscriptionData.invite_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline flex items-center"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 mr-2 text-blue-500"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {subscriptionData.invite_link}
                  </a>
                </div>
                <p className="text-sm text-gray-500 mt-2 flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-1 text-yellow-500"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                      clipRule="evenodd"
                    />
                  </svg>
                  This link is valid until{" "}
                  {formatDate(subscriptionData.invite_expires_at)} and can only
                  be used once.
                </p>
              </div>
            )}

            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                Subscription Details
              </h4>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">PRODUCT</p>
                    <p className="font-medium text-gray-800">{product.name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">EXPIRES ON</p>
                    <p className="font-medium text-gray-800">
                      {formatDate(subscriptionData?.subscription_expires_at)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center mt-6">
              <button onClick={() => navigate("/")} className="btn-primary">
                Back to Products
              </button>
            </div>
          </div>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="bg-white shadow-lg rounded-lg px-8 pt-6 pb-8 mb-4 border border-gray-100"
        >
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">
              Subscribe to {product.name}
            </h2>

            {product.description && (
              <div className="bg-purple-50 p-4 rounded-lg mb-4">
                <p className="text-gray-700">
                  <span className="font-medium text-purple-700">
                    About this product:
                  </span>{" "}
                  {product.description}
                </p>
              </div>
            )}

            {product.telegram_group && (
              <div className="flex items-center mb-4 bg-gray-50 p-3 rounded-lg">
                <div className="bg-purple-100 p-2 rounded-full mr-3">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-purple-600"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10c0 4.418-3.582 8-8 8s-8-3.582-8-8 3.582-8 8-8 8 3.582 8 8zm-3.5 0a.5.5 0 01-.5.5h-7a.5.5 0 010-1h7a.5.5 0 01.5.5z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <p className="text-gray-700">
                  <span className="font-medium">Telegram Group:</span>{" "}
                  {product.telegram_group.telegram_group_name}
                </p>
              </div>
            )}
          </div>

          <div className="mb-5">
            <label
              className="block text-gray-700 text-sm font-medium mb-2"
              htmlFor="email"
            >
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-gray-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                </svg>
              </div>
              <input
                className="shadow-sm appearance-none border border-gray-300 rounded-lg w-full py-3 px-4 pl-10 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="mb-6">
            <label
              className="block text-gray-700 text-sm font-medium mb-2"
              htmlFor="expirationDate"
            >
              Subscription Expiration (Optional)
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-gray-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <input
                className="shadow-sm appearance-none border border-gray-300 rounded-lg w-full py-3 px-4 pl-10 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                id="expirationDate"
                type="datetime-local"
                value={expirationDate}
                onChange={(e) => setExpirationDate(e.target.value)}
              />
            </div>
            <p className="text-sm text-gray-500 mt-1">
              If not specified, subscription will expire in 30 days
            </p>
          </div>

          <div className="mb-6">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={forceRenew}
                onChange={(e) => setForceRenew(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
              />
              <span className="ml-3 text-sm text-gray-700">
                Force renew - Cancel existing active subscription if any
              </span>
            </label>
            <p className="text-sm text-gray-500 mt-1 ml-7">
              Enable this to automatically cancel any existing active
              subscription for this user and product
            </p>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              className="btn-primary w-full md:w-auto"
              type="submit"
              disabled={submitting}
            >
              {submitting ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                "Subscribe Now"
              )}
            </button>
            <button
              type="button"
              onClick={() => navigate("/")}
              className="mt-3 md:mt-0 text-gray-600 hover:text-gray-800 font-medium py-3 px-6 rounded-lg border border-gray-300 hover:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:ring-offset-2 transition-colors w-full md:w-auto"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default SubscriptionForm