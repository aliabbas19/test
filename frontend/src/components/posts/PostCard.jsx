
const PostCard = ({ post, onDelete, onUpdate }) => {
  const { isAdmin } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [editContent, setEditContent] = useState(post.content)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!editContent.trim()) return
    setSaving(true)
    try {
      await onUpdate(post.id, editContent)
      setIsEditing(false)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="admin-post group relative">
      {isAdmin && (
        <div className="absolute top-4 left-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 p-1 rounded-lg shadow-sm backdrop-blur-sm">
          <button
            onClick={() => setIsEditing(true)}
            className="btn btn-xs btn-circle btn-ghost text-info"
            title="تعديل"
          >
            <i className="fa-solid fa-pen"></i>
          </button>
          <button
            onClick={() => onDelete(post.id)}
            className="btn btn-xs btn-circle btn-ghost text-error"
            title="حذف"
          >
            <i className="fa-solid fa-trash"></i>
          </button>
        </div>
      )}

      <div className="flex items-center p-4 bg-gray-50/80 border-b border-gray-100">
        <div className="bg-primary/10 p-2 rounded-full ml-3">
          <i className="fa-solid fa-bullhorn text-2xl text-primary"></i>
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-lg text-gray-800">إعلان إداري</span>
          <span className="text-sm text-gray-500 flex items-center gap-1">
            <i className="fa-solid fa-user-shield text-xs"></i>
            {post.full_name || "الإدارة"}
          </span>
        </div>
      </div>

      <div className="p-5 text-lg leading-relaxed whitespace-pre-wrap text-gray-700 min-h-[100px]">
        {isEditing ? (
          <div className="form-control animate-fade-in">
            <textarea
              className="textarea textarea-bordered w-full h-32 text-lg bg-white"
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
            ></textarea>
            <div className="flex justify-end gap-2 mt-2">
              <button
                className="btn btn-sm btn-primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving && <span className="loading loading-spinner loading-xs"></span>}
                حفظ
              </button>
              <button
                className="btn btn-sm btn-ghost"
                onClick={() => {
                  setIsEditing(false)
                  setEditContent(post.content)
                }}
              >
                إلغاء
              </button>
            </div>
          </div>
        ) : (
          post.content
        )}
      </div>

      <div className="px-5 py-3 bg-gray-50/80 border-t border-gray-100 text-sm text-gray-500 flex justify-between items-center" dir="ltr">

        <span>
          {isAdmin && <span className="text-xs bg-gray-200 px-2 py-0.5 rounded ml-2">ID: {post.id}</span>}
        </span>

        <span className="flex items-center gap-2">
          {formatTime(post.timestamp)} <i className="fa-regular fa-clock"></i>
        </span>
      </div>
    </div>
  )
}

export default PostCard

