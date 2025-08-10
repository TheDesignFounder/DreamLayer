import { MatrixJob, MatrixSettings, ImageResult } from "@/types/generationSettings";

const loadImage = (url: string): Promise<HTMLImageElement> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = (err) => reject(new Error(`Failed to load image at ${url}: ${err}`));
    img.src = url;
  });
};

const saveMatrixGridToServer = async (canvas: HTMLCanvasElement, matrixId: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    canvas.toBlob(async (blob) => {
      if (!blob) {
        reject(new Error('Failed to create blob from canvas'));
        return;
      }

      try {
        console.log('🔄 Sending Matrix grid to permanent server storage...');
        console.log('📊 Blob size:', blob.size, 'bytes');
        
        const reader = new FileReader();
        reader.onloadend = async () => {
          try {
            const base64Data = reader.result as string;
            console.log('📊 Base64 length:', base64Data.length);

            const response = await fetch('http://localhost:5001/api/save-matrix-grid', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                imageData: base64Data,
                matrixId: matrixId
              })
            });

            console.log('📡 Server response status:', response.status);
            
            if (!response.ok) {
              const errorText = await response.text();
              console.error('❌ Server error response:', errorText);
              throw new Error(`Server responded with ${response.status}: ${errorText}`);
            }

            const result = await response.json();
            console.log('📨 Server response:', result);
            
            if (result.status === 'success') {
              console.log('🎉 Matrix grid saved to permanent server storage:', result.url);
              console.log('📁 Filename:', result.filename);
              console.log('📏 File size:', result.filesize);
              console.log('💾 Storage type:', result.storage);
              
              try {
                const verifyResponse = await fetch(result.url);
                console.log('🔍 File verification:', verifyResponse.status, verifyResponse.ok);
                if (verifyResponse.ok) {
                  console.log('✅ File is immediately accessible from permanent storage');
                } else {
                  console.warn('⚠️ File not immediately accessible:', verifyResponse.statusText);
                }
              } catch (verifyError) {
                console.warn('⚠️ File verification failed:', verifyError);
              }
              
              resolve(result.url);
            } else {
              throw new Error(result.message || 'Unknown server error');
            }
          } catch (error) {
            console.error('❌ Error in server communication:', error);
            reject(error);
          }
        };
        
        reader.onerror = () => {
          reject(new Error('Failed to read blob as base64'));
        };
        
        reader.readAsDataURL(blob);
      } catch (error) {
        reject(error);
      }
    }, 'image/png');
  });
};

export const generateMatrixGrid = async (
  completedJobs: MatrixJob[],
  matrixSettings: MatrixSettings
): Promise<string> => {
  console.log('🎨 Starting matrix grid generation...');
  console.log('Jobs:', completedJobs);
  console.log('Settings:', matrixSettings);

  if (completedJobs.length === 0) {
    throw new Error('No images were generated to create a grid.');
  }

  const xValues = [...new Set(completedJobs.map(job => job.xValue).filter(v => v !== null))].sort();
  const yValues = [...new Set(completedJobs.map(job => job.yValue).filter(v => v !== null))].sort();
  const zValues = [...new Set(completedJobs.map(job => job.zValue).filter(v => v !== null))].sort();

  console.log('🔍 Extracted values:', { xValues, yValues, zValues });

  const hasXAxis = xValues.length > 1 && matrixSettings.xAxis?.name !== 'Nothing';
  const hasYAxis = yValues.length > 1 && matrixSettings.yAxis?.name !== 'Nothing';
  const hasZAxis = zValues.length > 1 && matrixSettings.zAxis?.name !== 'Nothing';

  console.log('🔍 Active axes:', { hasXAxis, hasYAxis, hasZAxis });

  const imagePromises = completedJobs.map(async (job) => {
    if (!job.result || job.result.length === 0) {
      throw new Error(`Job has no result images: ${JSON.stringify(job)}`);
    }
    const imageUrl = job.result[0].url;
    const loadedImage = await loadImage(imageUrl);
    return { job, image: loadedImage };
  });

  const imageResults = await Promise.all(imagePromises);
  const sampleImage = imageResults[0].image;
  const imageWidth = sampleImage.width;
  const imageHeight = sampleImage.height;

  const labelHeight = matrixSettings.drawLegend && hasXAxis ? 200 : 0;
  const labelWidth = matrixSettings.drawLegend && hasYAxis ? 250 : 0;
  const margin = 20;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  if (hasZAxis) {
    const gridCols = hasXAxis ? xValues.length : 1;
    const gridRows = hasYAxis ? yValues.length : 1;
    const zCount = zValues.length;

    const canvasWidth = (labelWidth + imageWidth * gridCols + margin * (gridCols + 1)) * zCount + margin * (zCount + 1);
    const canvasHeight = labelHeight + imageHeight * gridRows + margin * (gridRows + 1);

    canvas = document.createElement('canvas');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx = canvas.getContext('2d')!;

    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    for (let z = 0; z < zCount; z++) {
      const zValue = zValues[z];
      const zOffsetX = z * (labelWidth + imageWidth * gridCols + margin * (gridCols + 1)) + margin;

      if (matrixSettings.drawLegend && hasZAxis) {
        const zLabelX = zOffsetX + (labelWidth + imageWidth * gridCols) / 2;
        const zLabelY = 80;

        ctx.font = 'bold 72px Arial';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const zText = `${matrixSettings.zAxis?.name}: ${zValue}`;
        ctx.fillText(zText, zLabelX, zLabelY);
      }

      for (let y = 0; y < gridRows; y++) {
        for (let x = 0; x < gridCols; x++) {
          const xValue = hasXAxis ? xValues[x] : null;
          const yValue = hasYAxis ? yValues[y] : null;

          const matchingResult = imageResults.find(({ job }) => {
            const xMatch = !hasXAxis || job.xValue === xValue;
            const yMatch = !hasYAxis || job.yValue === yValue;
            const zMatch = !hasZAxis || job.zValue === zValue;
            return xMatch && yMatch && zMatch;
          });

          if (matchingResult) {
            const drawX = zOffsetX + labelWidth + x * imageWidth + margin * (x + 1);
            const drawY = labelHeight + y * imageHeight + margin * (y + 1);
            ctx.drawImage(matchingResult.image, drawX, drawY, imageWidth, imageHeight);
          }
        }
      }

      if (matrixSettings.drawLegend && hasXAxis) {
        ctx.font = 'bold 48px Arial';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let x = 0; x < gridCols; x++) {
          const labelX = zOffsetX + labelWidth + x * imageWidth + imageWidth / 2 + margin * (x + 1);
          const labelY = labelHeight - 60;
          const xText = `${matrixSettings.xAxis?.name}: ${xValues[x]}`;
          ctx.fillText(xText, labelX, labelY);
        }
      }

      if (matrixSettings.drawLegend && hasYAxis) {
        ctx.font = 'bold 48px Arial';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let y = 0; y < gridRows; y++) {
          const labelX = zOffsetX + labelWidth / 2;
          const labelY = labelHeight + y * imageHeight + imageHeight / 2 + margin * (y + 1);
          
          ctx.save();
          ctx.translate(labelX, labelY);
          ctx.rotate(-Math.PI / 2);
          const yText = `${matrixSettings.yAxis?.name}: ${yValues[y]}`;
          ctx.fillText(yText, 0, 0);
          ctx.restore();
        }
      }
    }

  } else {
    const gridCols = hasXAxis ? xValues.length : 1;
    const gridRows = hasYAxis ? yValues.length : 1;

    const canvasWidth = labelWidth + imageWidth * gridCols + margin * (gridCols + 1);
    const canvasHeight = labelHeight + imageHeight * gridRows + margin * (gridRows + 1);

    canvas = document.createElement('canvas');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx = canvas.getContext('2d')!;

    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    for (let y = 0; y < gridRows; y++) {
      for (let x = 0; x < gridCols; x++) {
        const xValue = hasXAxis ? xValues[x] : null;
        const yValue = hasYAxis ? yValues[y] : null;

        const matchingResult = imageResults.find(({ job }) => {
          const xMatch = !hasXAxis || job.xValue === xValue;
          const yMatch = !hasYAxis || job.yValue === yValue;
          return xMatch && yMatch;
        });

        if (matchingResult) {
          const drawX = labelWidth + x * imageWidth + margin * (x + 1);
          const drawY = labelHeight + y * imageHeight + margin * (y + 1);
          ctx.drawImage(matchingResult.image, drawX, drawY, imageWidth, imageHeight);
        }
      }
    }

    if (matrixSettings.drawLegend) {
      ctx.fillStyle = 'white';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      if (hasXAxis) {
        ctx.font = 'bold 56px Arial';
        for (let x = 0; x < gridCols; x++) {
          const labelX = labelWidth + x * imageWidth + imageWidth / 2 + margin * (x + 1);
          const labelY = labelHeight - 80;
          const xText = `${matrixSettings.xAxis?.name}: ${xValues[x]}`;
          ctx.fillText(xText, labelX, labelY);
        }
      }

      if (hasYAxis) {
        ctx.font = 'bold 56px Arial';
        for (let y = 0; y < gridRows; y++) {
          const labelX = labelWidth / 2;
          const labelY = labelHeight + y * imageHeight + imageHeight / 2 + margin * (y + 1);
          
          ctx.save();
          ctx.translate(labelX, labelY);
          ctx.rotate(-Math.PI / 2);
          const yText = `${matrixSettings.yAxis?.name}: ${yValues[y]}`;
          ctx.fillText(yText, 0, 0);
          ctx.restore();
        }
      }
    }
  }

  try {
    const matrixId = `matrix-grid-${Date.now()}`;
    console.log('🔄 Attempting to save Matrix grid to permanent storage with ID:', matrixId);
    
    const serverUrl = await saveMatrixGridToServer(canvas, matrixId);
    
    console.log('🎉 Matrix grid generated and saved to permanent server storage successfully');
    console.log('🔗 Permanent server URL:', serverUrl);
    
    try {
      console.log('🔍 Testing permanent URL accessibility...');
      const testResponse = await fetch(serverUrl);
      console.log('✅ Permanent URL accessibility test:', testResponse.status, testResponse.ok);
      
      if (testResponse.ok) {
        const blob = await testResponse.blob();
        console.log('📏 Retrieved blob size:', blob.size, 'bytes');
        console.log('📄 Retrieved blob type:', blob.type);
        console.log('💾 Matrix grid is now permanently stored and accessible');
      } else {
        console.warn('⚠️ Generated permanent URL is not immediately accessible:', testResponse.statusText);
      }
    } catch (testError) {
      console.warn('⚠️ Permanent URL accessibility test failed:', testError);
    }
    
    return serverUrl;
  } catch (error) {
    console.error('❌ Failed to save Matrix grid to permanent server storage:', error);
    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          console.log('⚠️ Using fallback blob URL (not persistent):', url);
          resolve(url);
        } else {
          reject(new Error('Failed to create blob from canvas'));
        }
      });
    });
  }
}; 