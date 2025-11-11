import { useEffect, useState } from 'react'
import './ProgressMonitor.css'

interface ProgressEvent {
  job_id: string
  stage: string
  progress: number
  message: string
}

interface ProgressMonitorProps {
  jobId: string | null
}

export function ProgressMonitor({ jobId }: ProgressMonitorProps) {
  const [events, setEvents] = useState<ProgressEvent[]>([])
  const [currentProgress, setCurrentProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState('')
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!jobId) {
      setEvents([])
      setCurrentProgress(0)
      setCurrentStage('')
      setIsConnected(false)
      return
    }

    // Connect to SSE endpoint
    const eventSource = new EventSource(`/api/events/job:${jobId}`)

    eventSource.onopen = () => {
      setIsConnected(true)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.event === 'progress') {
          const progressEvent: ProgressEvent = data.data
          setEvents((prev) => [...prev, progressEvent])
          setCurrentProgress(progressEvent.progress * 100)
          setCurrentStage(progressEvent.stage)
        }
      } catch (err) {
        console.error('Failed to parse SSE event:', err)
      }
    }

    eventSource.onerror = () => {
      setIsConnected(false)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [jobId])

  if (!jobId) {
    return (
      <div className="progress-monitor">
        <div className="monitor-placeholder">No active generation</div>
      </div>
    )
  }

  return (
    <div className="progress-monitor">
      <div className="monitor-header">
        <h4>Generation Progress</h4>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar" style={{ width: `${currentProgress}%` }} />
        <div className="progress-text">{Math.round(currentProgress)}%</div>
      </div>

      {currentStage && (
        <div className="current-stage">
          Stage: <span className="stage-name">{currentStage}</span>
        </div>
      )}

      <div className="event-log">
        <h5>Event Log</h5>
        <div className="event-list">
          {events.map((event, i) => (
            <div key={i} className="event-item">
              <span className="event-stage">[{event.stage}]</span>
              <span className="event-message">{event.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
