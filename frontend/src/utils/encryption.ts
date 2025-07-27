import CryptoJS from 'crypto-js';

export const encryptFile = async (file: File, key: string): Promise<File> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const fileData = event.target?.result as ArrayBuffer;
        const wordArray = CryptoJS.lib.WordArray.create(fileData);
        
        // Generate a random IV
        const iv = CryptoJS.lib.WordArray.random(16);
        
        // Encrypt the file data
        const encrypted = CryptoJS.AES.encrypt(wordArray, key, {
          iv: iv,
          mode: CryptoJS.mode.CBC,
          padding: CryptoJS.pad.Pkcs7
        });
        
        // Combine IV and encrypted data
        const combined = iv.concat(encrypted.ciphertext);
        
        // Convert to Blob
        const encryptedBlob = new Blob([combined.toString(CryptoJS.enc.Hex)], {
          type: 'application/octet-stream'
        });
        
        // Create new File object
        const encryptedFile = new File([encryptedBlob], file.name, {
          type: 'application/octet-stream'
        });
        
        resolve(encryptedFile);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    
    reader.readAsArrayBuffer(file);
  });
};

export const decryptFile = async (encryptedData: ArrayBuffer, key: string, iv: string): Promise<ArrayBuffer> => {
  return new Promise((resolve, reject) => {
    try {
      // For now, return the original data as a placeholder
      // This will be implemented properly in a production environment
      resolve(encryptedData);
    } catch (error) {
      reject(error);
    }
  });
}; 