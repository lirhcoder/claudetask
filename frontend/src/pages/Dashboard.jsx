import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Modal, Input, Form, message, Spin, Empty } from 'antd'
import { PlusOutlined, FolderOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { projectApi } from '../services/api'
import ProjectManager from '../components/ProjectManager'

const Dashboard = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalVisible, setModalVisible] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const data = await projectApi.listProjects()
      setProjects(data.projects)
    } catch (error) {
      message.error('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async (values) => {
    try {
      setCreating(true)
      await projectApi.createProject(values.name, true)
      message.success('Project created successfully')
      setModalVisible(false)
      form.resetFields()
      loadProjects()
    } catch (error) {
      message.error(error.response?.data?.error || 'Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  const handleProjectClick = (projectName) => {
    navigate(`/project/${projectName}`)
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Projects</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          New Project
        </Button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
        </div>
      ) : projects.length === 0 ? (
        <Empty
          description="No projects yet"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={() => setModalVisible(true)}>
            Create First Project
          </Button>
        </Empty>
      ) : (
        <Row gutter={[16, 16]}>
          {projects.map((project) => (
            <Col xs={24} sm={12} md={8} lg={6} key={project.name}>
              <ProjectManager
                project={project}
                onProjectUpdate={loadProjects}
                onProjectDelete={(name) => {
                  // 这里可以添加删除项目的API调用
                  message.info(`删除项目功能需要后端API支持`);
                  loadProjects();
                }}
              />
            </Col>
          ))}
        </Row>
      )}

      <Modal
        title="Create New Project"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateProject}
        >
          <Form.Item
            name="name"
            label="Project Name"
            rules={[
              { required: true, message: 'Please enter project name' },
              { pattern: /^[a-zA-Z0-9_-]+$/, message: 'Only letters, numbers, - and _ allowed' }
            ]}
          >
            <Input placeholder="my-awesome-project" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={creating} block>
              Create Project
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Dashboard