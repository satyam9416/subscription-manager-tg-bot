import { useState, useEffect } from "react";
import {
  getGroups,
  getProducts,
  mapProductToGroup,
  unmapProduct,
  getUnmappedGroups,
  removeBotAndDeleteGroup,
} from "../../services/api";

function Groups() {
  const [groups, setGroups] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [showOnlyUnmapped, setShowOnlyUnmapped] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [roleFilter, setRoleFilter] = useState("");

  const fetchData = async () => {
    try {
      const [productsResponse] = await Promise.all([getProducts()]);

      // Get either all groups or only unmapped groups based on filter
      const groupsResponse = showOnlyUnmapped
        ? await getUnmappedGroups()
        : await getGroups({
            status: statusFilter || undefined,
            role: roleFilter || undefined,
          });

      setGroups(groupsResponse.data);
      setProducts(productsResponse.data);
      setLoading(false);
    } catch (err) {
      setError("Failed to load data. Please try again later.");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [showOnlyUnmapped, statusFilter, roleFilter]);

  const handleOpenModal = (group) => {
    // Prevent opening modal for inactive groups
    if (!group.is_active) return;

    setSelectedGroup(group);
    setSelectedProduct("");
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedGroup(null);
  };

  const handleMapProduct = async (e) => {
    e.preventDefault();

    if (!selectedProduct) {
      setError("Please select a product");
      return;
    }

    try {
      await mapProductToGroup(selectedProduct, {
        telegram_group_id: selectedGroup.telegram_group_id,
        telegram_group_name: selectedGroup.telegram_group_name,
      });

      handleCloseModal();
      fetchData();
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Failed to map product to group. Please try again."
      );
    }
  };

  const handleUnmapProduct = async (productId) => {
    if (
      window.confirm(
        "Are you sure you want to unmap this product from the group?"
      )
    ) {
      try {
        await unmapProduct(productId);
        fetchData();
      } catch (err) {
        setError(
          err.response?.data?.message ||
            "Failed to unmap product. Please try again."
        );
      }
    }
  };

  const handleRemoveBotAndDelete = async (telegramGroupId) => {
    if (
      window.confirm(
        "Are you sure you want to remove the bot from this group and delete it from the system?"
      )
    ) {
      try {
        await removeBotAndDeleteGroup(telegramGroupId);
        fetchData();
      } catch (err) {
        setError(
          err.response?.data?.message ||
            "Failed to remove bot and delete group. Please try again."
        );
      }
    }
  };

  // Filter out products that are already mapped to a group
  const getUnmappedProducts = () => {
    return products.filter((product) => !product.telegram_group);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading groups...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Manage Telegram Groups
        </h1>
        <div className="flex items-center space-x-4">
          <label className="mr-2">
            <input
              type="checkbox"
              checked={showOnlyUnmapped}
              onChange={() => setShowOnlyUnmapped(!showOnlyUnmapped)}
              className="mr-1"
            />
            Show only unmapped groups
          </label>
          <div>
            <label className="text-sm text-gray-600 mr-2">Status</label>
            <select
              className="border rounded px-2 py-1"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-600 mr-2">Bot Role</label>
            <select
              className="border rounded px-2 py-1"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="">All</option>
              <option value="member">Member</option>
              <option value="administrator">Administrator</option>
              <option value="left">Left</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Group Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Group ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Bot Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mapped Product
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {groups.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  No groups available. Add the bot to a Telegram group first.
                </td>
              </tr>
            ) : (
              groups.map((group) => (
                <tr key={group.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {group.telegram_group_name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {group.telegram_group_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {group.bot_role || "-"}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {group.is_active ? (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Active
                      </span>
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {group.product ? (
                      <div className="text-sm text-gray-900">
                        {group.product.name}
                      </div>
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        Not Mapped
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {group.product ? (
                      <button
                        onClick={() => handleUnmapProduct(group.product.id)}
                        className="text-red-600 hover:text-red-900 mr-4"
                      >
                        Unmap
                      </button>
                    ) : (
                      <button
                        onClick={() => handleOpenModal(group)}
                        className={`text-blue-600 hover:text-blue-900 ${
                          !group.is_active
                            ? "opacity-50 cursor-not-allowed"
                            : ""
                        }`}
                        disabled={!group.is_active}
                        title={
                          !group.is_active
                            ? "Inactive groups cannot be mapped to products"
                            : ""
                        }
                      >
                        Map to Product
                      </button>
                    )}
                    <button
                      onClick={() =>
                        handleRemoveBotAndDelete(group.telegram_group_id)
                      }
                      className="text-red-600 hover:text-red-900 ml-4"
                    >
                      Remove Bot & Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {isModalOpen && selectedGroup && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Map Group to Product</h2>

            <p className="mb-4">
              <span className="font-bold">Group:</span>{" "}
              {selectedGroup.telegram_group_name}
            </p>

            <form onSubmit={handleMapProduct}>
              <div className="mb-6">
                <label
                  className="block text-gray-700 text-sm font-bold mb-2"
                  htmlFor="product"
                >
                  Select Product
                </label>
                <select
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="product"
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  required
                >
                  <option value="">-- Select a Product --</option>
                  {getUnmappedProducts().map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
                {getUnmappedProducts().length === 0 && (
                  <p className="text-red-500 text-xs italic mt-2">
                    No unmapped products available. Create a new product first.
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <button
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  type="submit"
                  disabled={getUnmappedProducts().length === 0}
                >
                  Map
                </button>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Groups;
