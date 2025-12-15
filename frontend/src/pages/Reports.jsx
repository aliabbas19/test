import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

const Reports = () => {
  const { isAdmin } = useAuth()
  const navigate = useNavigate()
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedClass, setSelectedClass] = useState('')

  useEffect(() => {
    if (isAdmin) {
      fetchReports()
    }
  }, [isAdmin, selectedClass])

  const fetchReports = async () => {
    try {
      const params = selectedClass ? { class_name: selectedClass } : {}
      const response = await api.get('/api/reports/students', { params })
      setReportData(response.data)
    } catch (error) {
      console.error('Failed to fetch reports:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!isAdmin) {
      navigate('/')
    }
  }, [isAdmin, navigate])

  if (!isAdmin) {
    return null
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  if (!reportData) {
    return <div>لا توجد بيانات</div>
  }

  const { all_classes, selected_class, all_criteria, report_data } = reportData

  return (
    <div>
      <div className="ship-frame text-2xl lg:text-3xl mb-8 mx-auto w-fit">
        <span className="animate-text-gradient bg-gradient-to-r from-blue-600 via-primary to-blue-600 bg-[length:200%_auto] bg-clip-text text-transparent">
          تقارير نشاط الطلاب
        </span>
      </div>

      {/* Filter Section */}
      <div className="glass-effect p-6 rounded-xl mb-8">
        <div className="flex flex-col md:flex-row items-center gap-4 justify-between">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <i className="fa-solid fa-filter text-primary"></i> فلترة حسب الصف
          </h3>
          <div className="flex gap-4 w-full md:w-auto">
            <select
              className="select select-bordered bg-white/50 flex-1 w-full md:w-64"
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
            >
              <option value="">كل الصفوف</option>
              {all_classes.map((className) => (
                <option key={className} value={className}>
                  {className}
                </option>
              ))}
            </select>
            <button
              className="btn btn-primary btn-outline"
              onClick={() => setSelectedClass('')}
            >
              عرض الكل
            </button>
          </div>
        </div>
      </div>

      {/* Reports */}
      {report_data && report_data.length > 0 ? (
        <div className="space-y-8">
          {report_data.map((student) => (
            <div key={student.id} className="glass-effect rounded-xl overflow-hidden animate-fade-in-up">
              <div className="bg-gradient-to-r from-primary/10 to-transparent p-4 border-b border-primary/10 flex flex-col md:flex-row justify-between items-center gap-4">
                <h4 className="text-xl font-bold flex items-center gap-2">
                  <i className="fa-solid fa-user-graduate text-primary"></i> {student.full_name || student.username}
                </h4>
                <div className="badge badge-primary badge-lg badge-outline">
                  {student.class_name || 'غير محدد'} - {student.section_name || 'غير محدد'}
                </div>
              </div>
              <div className="p-6">
                {/* Weekly Activity Summary */}
                <h5 className="font-bold mb-4 flex items-center gap-2 text-gray-600">
                  <i className="fa-solid fa-chart-simple"></i> ملخص النشاط الأسبوعي
                </h5>
                <div className="grid grid-cols-3 gap-4 mb-8">
                  <div className="stat bg-white/40 rounded-xl border border-white/50 text-center py-4">
                    <div className="stat-title mb-1 text-sm md:text-base">الفيديوهات</div>
                    <div className="stat-value text-2xl text-primary">
                      {student.weekly_activity?.uploads || 0}
                    </div>
                  </div>
                  <div className="stat bg-white/40 rounded-xl border border-white/50 text-center py-4">
                    <div className="stat-title mb-1 text-sm md:text-base">التعليقات</div>
                    <div className="stat-value text-2xl text-secondary">
                      {student.weekly_activity?.comments || 0}
                    </div>
                  </div>
                  <div className="stat bg-white/40 rounded-xl border border-white/50 text-center py-4">
                    <div className="stat-title mb-1 text-sm md:text-base">بطل الأسبوع</div>
                    <div className="stat-value text-2xl">
                      {student.weekly_activity?.is_champion ? (
                        <span className="flex items-center justify-center gap-1">
                          <i className="fa-solid fa-mask text-purple-600 animate-bounce"></i>
                          <i className="fa-solid fa-trophy text-yellow-500"></i>
                        </span>
                      ) : '-'}
                    </div>
                  </div>
                </div>

                {/* منهجي Videos */}
                <div className="border-t border-gray-200/50 my-6"></div>
                <h5 className="font-bold mb-4 flex items-center gap-2 text-gray-700">
                  <i className="fa-solid fa-book-open text-info"></i> الفيديوهات المنهجية
                </h5>
                {student.videos_manhaji && student.videos_manhaji.length > 0 ? (
                  <div className="overflow-x-auto rounded-lg border border-gray-200/50">
                    <table className="table w-full">
                      <thead className="bg-primary/5">
                        <tr>
                          <th>عنوان الفيديو</th>
                          <th>تاريخ الرفع</th>
                          {all_criteria['منهجي']?.map((criterion) => (
                            <th key={criterion.id} title={criterion.name}>
                              <span className="tooltip" data-tip={criterion.name}>{criterion.name}</span>
                            </th>
                          ))}
                          <th>المجموع</th>
                        </tr>
                      </thead>
                      <tbody>
                        {student.videos_manhaji.map((video) => (
                          <tr key={video.id} className="hover:bg-white/30">
                            <td className="font-medium">{video.title}</td>
                            <td className="text-sm opacity-70">{new Date(video.timestamp).toLocaleDateString('ar-EG')}</td>
                            {all_criteria['منهجي']?.map((criterion) => (
                              <td key={criterion.id}>
                                {video.ratings?.[criterion.key] === 1 ? (
                                  <i className="fa-solid fa-check text-success"></i>
                                ) : (
                                  <i className="fa-solid fa-xmark text-error opacity-30"></i>
                                )}
                              </td>
                            ))}
                            <td>
                              <div className="radial-progress text-primary text-xs font-bold" style={{ "--value": (video.total_stars / (all_criteria['منهجي']?.length || 1) * 100), "--size": "2rem" }}>
                                {video.total_stars}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-6 bg-gray-50/50 rounded-lg text-gray-400 text-sm">
                    لم يقم هذا الطالب برفع أي فيديوهات منهجية بعد.
                  </div>
                )}

                {/* اثرائي Videos */}
                <div className="border-t border-gray-200/50 my-6"></div>
                <h5 className="font-bold mb-4 flex items-center gap-2 text-gray-700">
                  <i className="fa-solid fa-lightbulb text-warning"></i> الفيديوهات الإثرائية
                </h5>
                {student.videos_ithrai && student.videos_ithrai.length > 0 ? (
                  <div className="overflow-x-auto rounded-lg border border-gray-200/50">
                    <table className="table w-full">
                      <thead className="bg-warning/5">
                        <tr>
                          <th>عنوان الفيديو</th>
                          <th>التاريخ</th>
                          {all_criteria['اثرائي']?.map((criterion) => (
                            <th key={criterion.id} title={criterion.name}>
                              <span className="tooltip" data-tip={criterion.name}>{criterion.name}</span>
                            </th>
                          ))}
                          <th>المجموع</th>
                        </tr>
                      </thead>
                      <tbody>
                        {student.videos_ithrai.map((video) => (
                          <tr key={video.id} className="hover:bg-white/30">
                            <td className="font-medium">{video.title}</td>
                            <td className="text-sm opacity-70">{new Date(video.timestamp).toLocaleDateString('ar-EG')}</td>
                            {all_criteria['اثرائي']?.map((criterion) => (
                              <td key={criterion.id}>
                                {video.ratings?.[criterion.key] === 1 ? (
                                  <i className="fa-solid fa-check text-success"></i>
                                ) : (
                                  <i className="fa-solid fa-xmark text-error opacity-30"></i>
                                )}
                              </td>
                            ))}
                            <td>
                              <div className="radial-progress text-warning text-xs font-bold" style={{ "--value": (video.total_stars / (all_criteria['اثرائي']?.length || 1) * 100), "--size": "2rem" }}>
                                {video.total_stars}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-6 bg-gray-50/50 rounded-lg text-gray-400 text-sm">
                    لم يقم هذا الطالب برفع أي فيديوهات إثرائية بعد.
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 glass-effect rounded-xl">
          <i className="fa-solid fa-folder-open text-6xl text-gray-300 mb-4"></i>
          <p className="text-gray-500 text-lg">لا توجد بيانات لعرضها تطابق معايير البحث.</p>
        </div>
      )}
    </div>
  )
}

export default Reports

