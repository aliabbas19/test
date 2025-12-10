import ProfileImage from '../common/ProfileImage'
import { formatTime } from '../../utils/helpers'

const PostCard = ({ post }) => {
  return (
    <div className="admin-post">
      <div className="flex items-center p-4 bg-gray-50/80 border-b border-gray-100">
        <i className="fa-solid fa-bullhorn text-2xl text-primary ml-3"></i>
        <div className="flex flex-col">
          <span className="font-bold text-lg text-gray-800">إعلان إداري</span>
          <span className="text-sm text-gray-500">{post.full_name || "الإدارة"}</span>
        </div>
      </div>
      <div className="p-5 text-lg leading-relaxed whitespace-pre-wrap text-gray-700">
        {post.content}
      </div>
      <div className="px-5 py-3 bg-gray-50/80 border-t border-gray-100 text-sm text-gray-500 text-left" dir="ltr">
        <i className="fa-regular fa-clock mr-2"></i> {formatTime(post.timestamp)}
      </div>
    </div>
  )
}

export default PostCard

