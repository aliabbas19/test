import { useState, useEffect } from 'react'
import api from '../services/api'
import StudentManagement from '../components/admin/StudentManagement'

const Students = () => {
  return (
    <div>
      <div className="ship-frame text-3xl lg:text-4xl mb-8 mx-auto w-fit">
        <span className="animate-text-gradient bg-gradient-to-r from-blue-500 via-primary to-blue-500 bg-[length:200%_auto] bg-clip-text text-transparent">
          إدارة الطلاب
        </span>
      </div>
      <StudentManagement />
    </div>
  )
}

export default Students

