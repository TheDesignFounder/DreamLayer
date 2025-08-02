import React from "react";
import { render, fireEvent, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { useImg2ImgGalleryStore } from "@/stores/useImg2ImgGalleryStore";
import ImageUploader from "./ImageUploader";

jest.mock("@/stores/useImg2ImgGalleryStore");

describe("ImageUploader - Mask Upload", () => {
  let setMaskFile: jest.Mock;
  let setMaskPreview: jest.Mock;
  let setInputImage: jest.Mock;

  beforeEach(() => {
    setMaskFile = jest.fn();
    setMaskPreview = jest.fn();
    setInputImage = jest.fn();
    (useImg2ImgGalleryStore as jest.Mock).mockReturnValue({
      inputImage: null,
      setInputImage,
      maskFile: null,
      maskPreview: null,
      setMaskFile,
      setMaskPreview,
    });
  });

  function createFile(name: string, type: string, size: number) {
    const file = new File(["a".repeat(size)], name, { type });
    Object.defineProperty(file, "size", { value: size });
    return file;
  }

  it("accepts a valid PNG mask and updates preview/state", async () => {
    // Mock FileReader
    const addEventListener = jest.fn((_, cb) => cb());
    const readAsDataURL = jest.fn(function () {
      this.result = "data:image/png;base64,MOCK";
      this.onload({ target: this });
    });
    // @ts-ignore
    window.FileReader = jest.fn(() => ({
      addEventListener,
      readAsDataURL,
      onload: null,
      result: "data:image/png;base64,MOCK",
    }));

    render(<ImageUploader activeImg2ImgTool="inpaint-upload" />);
    const fileInput = screen
      .getByText("Browse Files")
      .closest("label")
      .querySelector('input[type="file"]');
    const file = createFile("mask.png", "image/png", 1024);
    fireEvent.change(fileInput!, { target: { files: [file] } });

    await waitFor(() => {
      expect(setMaskFile).toHaveBeenCalledWith(file);
      expect(setMaskPreview).toHaveBeenCalled();
    });
  });

  it("rejects non-PNG files", async () => {
    render(<ImageUploader activeImg2ImgTool="inpaint-upload" />);
    const fileInput = screen
      .getByText("Browse Files")
      .closest("label")
      .querySelector('input[type="file"]');
    const file = createFile("mask.jpg", "image/jpeg", 1024);
    fireEvent.change(fileInput!, { target: { files: [file] } });
    await waitFor(() => {
      expect(
        screen.getByText("Only PNG files are accepted.")
      ).toBeInTheDocument();
      expect(setMaskFile).toHaveBeenCalledWith(null);
      expect(setMaskPreview).toHaveBeenCalledWith(null);
    });
  });

  it("rejects files over 10MB", async () => {
    render(<ImageUploader activeImg2ImgTool="inpaint-upload" />);
    const fileInput = screen
      .getByText("Browse Files")
      .closest("label")
      .querySelector('input[type="file"]');
    const file = createFile("mask.png", "image/png", 11 * 1024 * 1024);
    fireEvent.change(fileInput!, { target: { files: [file] } });
    await waitFor(() => {
      expect(
        screen.getByText("File size must be 10 MB or less.")
      ).toBeInTheDocument();
      expect(setMaskFile).toHaveBeenCalledWith(null);
      expect(setMaskPreview).toHaveBeenCalledWith(null);
    });
  });

  it("clears the mask and error", async () => {
    (useImg2ImgGalleryStore as jest.Mock).mockReturnValue({
      inputImage: null,
      setInputImage,
      maskFile: new File(["a"], "mask.png", { type: "image/png" }),
      maskPreview: "data:image/png;base64,MOCK",
      setMaskFile,
      setMaskPreview,
    });
    render(<ImageUploader activeImg2ImgTool="inpaint-upload" />);
    const clearBtn = screen.getByText("Clear");
    fireEvent.click(clearBtn);
    await waitFor(() => {
      expect(setMaskFile).toHaveBeenCalledWith(null);
      expect(setMaskPreview).toHaveBeenCalledWith(null);
    });
  });
});
