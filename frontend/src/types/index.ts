export interface FileInfo {
  id: number;
  original_filename: string;
  filename: string;
  file_size: number;
  content_type: string;
  upload_date: string;
  processing_status: string;
  is_processed: boolean;
}

export interface UploadResponse {
  message: string;
  file_id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  upload_date: string;
  status: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
} 