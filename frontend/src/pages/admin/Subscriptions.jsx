import { useState, useEffect, useRef } from "react";
import {
  getSubscriptions,
  getProducts,
  cancelSubscription,
} from "../../services/api";
import { debounce } from "lodash";

function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [products, setProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const tableRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    perPage: 10,
    total: 0,
    pages: 0,
  });
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState({
    by: "created_at",
    order: "desc",
  });
  const [filter, setFilter] = useState({
    status: "",
    productId: "",
    userId: "",
  });

  const fetchData = async () => {
    try {
      // Save current scroll position
      const scrollPosition = tableRef.current ? tableRef.current.scrollTop : 0;

      setLoading(true);

      // Build query parameters
      const params = new URLSearchParams();
      params.append("page", pagination.page);
      params.append("per_page", pagination.perPage);
      params.append("sort_by", sort.by);
      params.append("sort_order", sort.order);

      if (search) {
        params.append("search", search);
      }

      if (filter.status) {
        params.append("status", filter.status);
      }

      if (filter.productId) {
        params.append("product_id", filter.productId);
      }

      if (filter.userId) {
        params.append("user_id", filter.userId);
      }

      const [subscriptionsResponse, productsResponse] = await Promise.all([
        getSubscriptions(params),
        getProducts(),
      ]);

      setSubscriptions(subscriptionsResponse.data.items);
      setPagination({
        page: subscriptionsResponse.data.page,
        perPage: subscriptionsResponse.data.per_page,
        total: subscriptionsResponse.data.total,
        pages: subscriptionsResponse.data.pages,
      });
      setProducts(productsResponse.data);
      setLoading(false);

      // Restore scroll position after data is loaded
      setTimeout(() => {
        if (tableRef.current) {
          tableRef.current.scrollTop = scrollPosition;
        }
      }, 0);
    } catch (err) {
      setError("Failed to load data. Please try again later.");
      setLoading(false);
    }
  };

  // Debounced search function
  const debouncedSearch = debounce(() => {
    setPagination((prev) => ({ ...prev, page: 1 })); // Reset to first page on search
    fetchData();
  }, 500);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.page, pagination.perPage, sort.by, sort.order]);

  useEffect(() => {
    debouncedSearch();
    return () => debouncedSearch.cancel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, filter.status, filter.productId, filter.userId]);

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Get status badge color
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "pending_join":
        return "bg-yellow-100 text-yellow-800";
      case "expired":
        return "bg-red-100 text-red-800";
      case "cancelled":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  // Filter subscriptions based on selected filters
  const filteredSubscriptions = subscriptions.filter((subscription) => {
    if (filter.status && subscription.status !== filter.status) {
      return false;
    }
    if (
      filter.productId &&
      subscription.product.id.toString() !== filter.productId
    ) {
      return false;
    }
    return true;
  });

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
  };

  const handleSortChange = (column) => {
    setSort((prev) => {
      if (prev.by === column) {
        // Toggle sort order if clicking the same column
        return { by: column, order: prev.order === "asc" ? "desc" : "asc" };
      }
      // Default to descending order for new column
      return { by: column, order: "desc" };
    });
  };

  const handlePageChange = (newPage) => {
    setPagination((prev) => ({ ...prev, page: newPage }));
  };

  const handlePerPageChange = (e) => {
    const newPerPage = parseInt(e.target.value);
    setPagination((prev) => ({ ...prev, page: 1, perPage: newPerPage }));
  };

  const handleCancelSubscription = async (id) => {
    if (window.confirm("Are you sure you want to cancel this subscription?")) {
      try {
        await cancelSubscription(id);
        // Refresh the subscriptions list
        fetchData();
      } catch (err) {
        setError("Failed to cancel subscription. Please try again.");
      }
    }
  };

  // Generate pagination buttons
  const renderPagination = () => {
    const pages = [];
    const maxButtons = 5;
    let startPage = Math.max(1, pagination.page - Math.floor(maxButtons / 2));
    let endPage = Math.min(pagination.pages, startPage + maxButtons - 1);

    if (endPage - startPage + 1 < maxButtons) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }

    // Previous button
    pages.push(
      <button
        key="prev"
        onClick={() => handlePageChange(Math.max(1, pagination.page - 1))}
        disabled={pagination.page === 1}
        className="px-3 py-1 border rounded mx-1 bg-white disabled:opacity-50"
      >
        &laquo;
      </button>
    );

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`px-3 py-1 border rounded mx-1 ${
            pagination.page === i ? "bg-blue-500 text-white" : "bg-white"
          }`}
        >
          {i}
        </button>
      );
    }

    // Next button
    pages.push(
      <button
        key="next"
        onClick={() =>
          handlePageChange(Math.min(pagination.pages, pagination.page + 1))
        }
        disabled={pagination.page === pagination.pages}
        className="px-3 py-1 border rounded mx-1 bg-white disabled:opacity-50"
      >
        &raquo;
      </button>
    );

    return pages;
  };

  // Get sort indicator
  const getSortIndicator = (column) => {
    if (sort.by !== column) return null;
    return sort.order === "asc" ? " ▲" : " ▼";
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        Manage Subscriptions
      </h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="flex flex-wrap gap-4">
          <div className="w-full md:w-1/3">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="search"
            >
              Search by Email
            </label>
            <input
              type="text"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="search"
              placeholder="Search by email..."
              value={search}
              onChange={handleSearchChange}
            />
          </div>

          <div className="w-full md:w-auto">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="status"
            >
              Filter by Status
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="status"
              name="status"
              value={filter.status}
              onChange={handleFilterChange}
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="pending_join">Pending Join</option>
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="w-full md:w-auto">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="productId"
            >
              Filter by Product
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="productId"
              name="productId"
              value={filter.productId}
              onChange={handleFilterChange}
            >
              <option value="">All Products</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          {/* <div className="w-full md:w-auto">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="userId"
            >
              Filter by User
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="userId"
              name="userId"
              value={filter.userId}
              onChange={handleFilterChange}
            >
              <option value="">All Users</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.email}
                </option>
              ))}
            </select>
          </div> */}

          <div className="w-full md:w-auto">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="perPage"
            >
              Items per page
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="perPage"
              value={pagination.perPage}
              onChange={handlePerPageChange}
            >
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-600">Loading subscriptions...</div>
        </div>
      ) : (
        <div
          className="bg-white shadow-md rounded-lg overflow-hidden"
          ref={tableRef}
        >
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSortChange("email")}
                >
                  User {getSortIndicator("email")}
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSortChange("product_id")}
                >
                  Product {getSortIndicator("product_id")}
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSortChange("status")}
                >
                  Status {getSortIndicator("status")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Telegram Info
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invite Link
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSortChange("subscription_expires_at")}
                >
                  Expires {getSortIndicator("subscription_expires_at")}
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSortChange("created_at")}
                >
                  Created {getSortIndicator("created_at")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {subscriptions.length === 0 ? (
                <tr>
                  <td
                    colSpan="8"
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    No subscriptions available.
                  </td>
                </tr>
              ) : (
                subscriptions.map((subscription) => (
                  <tr key={subscription.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {subscription.user_email}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {subscription.product.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(
                          subscription.status
                        )}`}
                      >
                        {subscription.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {subscription.user_tg_id ? (
                        <div>
                          <div className="text-sm text-gray-900">
                            ID: {subscription.user_tg_id}
                          </div>
                          {subscription.user_tg_username && (
                            <div className="text-sm text-gray-500">
                              @{subscription.user_tg_username}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">
                          Not joined yet
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {subscription.invite_link_url ? (
                        <div className="text-sm text-gray-500 truncate max-w-xs">
                          <a
                            href={subscription.invite_link_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            View Link
                          </a>
                          <div className="text-xs">
                            Expires:{" "}
                            {formatDate(subscription.invite_link_expires_at)}
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">No link</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatDate(subscription.subscription_expires_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatDate(subscription.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {subscription.status !== "cancelled" && (
                        <button
                          onClick={() =>
                            handleCancelSubscription(subscription.id)
                          }
                          className="text-sm bg-red-100 hover:bg-red-200 text-red-800 py-1 px-3 rounded"
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      <div className="mt-6 flex justify-between items-center">
        <div className="text-sm text-gray-700">
          Showing{" "}
          {subscriptions.length > 0
            ? (pagination.page - 1) * pagination.perPage + 1
            : 0}{" "}
          to {Math.min(pagination.page * pagination.perPage, pagination.total)}{" "}
          of {pagination.total} entries
        </div>
        <div className="flex">{renderPagination()}</div>
      </div>
    </div>
  );
}

export default Subscriptions;
