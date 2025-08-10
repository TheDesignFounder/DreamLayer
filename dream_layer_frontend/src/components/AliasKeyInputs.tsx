import React, { useState } from "react";
import { addAPIBasedModel } from "@/services/modelService";
import { CircleCheck, Eye, EyeOff, Loader2 } from "lucide-react";

const fields = [
  {
    name: "Flux - Black Forest Lab",
    alias: "BFL_API_KEY",
    placeholder: "Enter Flux API Key",
    docs: "https://docs.bfl.ai/quick_start/create_account",
  },
  {
    name: "Dall-E Model - OpenAI",
    alias: "OPENAI_API_KEY",
    placeholder: "Enter Dall-E API Key",
    docs: "https://platform.openai.com/docs/quickstart?api-mode=responses",
  },
  {
    name: "Ideogram Model",
    alias: "IDEOGRAM_API_KEY",
    placeholder: "Enter Ideogram API Key",
    docs: "https://developer.ideogram.ai/ideogram-api/api-setup",
  },
];

const ApiKeysForm: React.FC = () => {
  const [keys, setKeys] = useState<string[]>(["", "", ""]);
  const [submitted, setSubmitted] = useState<boolean[]>([false, false, false]);
  const [loading, setLoading] = useState<boolean[]>([false, false, false]);
  const [showText, setShowText] = useState<boolean[]>([false, false, false]);

  const handleChange = (index: number, value: string) => {
    setKeys((prev) => {
      const updated = [...prev];
      updated[index] = value;
      return updated;
    });
  };

  const handleSubmit = async (index: number) => {
    const alias = fields[index].alias;
    const apiKey = keys[index];

    setLoading((prev) => {
      const updated = [...prev];
      updated[index] = true;
      return updated;
    });

    const success = await addAPIBasedModel(alias, apiKey);

    setLoading((prev) => {
      const updated = [...prev];
      updated[index] = false;
      return updated;
    });

    if (success) {
      setSubmitted((prev) => {
        const updated = [...prev];
        updated[index] = true;
        return updated;
      });
    } else {
      console.error("Failed to submit API key.");
    }
  };

  const toggleShowText = (index: number) => {
    setShowText((prev) => {
      const updated = [...prev];
      updated[index] = !updated[index];
      return updated;
    });
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      {fields.map((field, idx) => (
        <div
          key={field.name}
          className="flex flex-col sm:flex-row sm:items-center gap-2"
        >
          <label className="w-full sm:w-48 text-sm font-medium whitespace-nowrap">
            {field.name}
            <a
              href={field.docs}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-1 text-xs text-blue-600 underline"
            >
              (Docs)
            </a>
          </label>

          <div className="relative w-full sm:w-72">
            <input
              type={showText[idx] ? "text" : "password"}
              value={keys[idx]}
              onChange={(e) => handleChange(idx, e.target.value)}
              placeholder={field.placeholder}
              className="w-full py-1 pr-10 pl-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              disabled={submitted[idx]}
            />
            <button
              type="button"
              onClick={() => toggleShowText(idx)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
              tabIndex={-1}
            >
              {showText[idx] ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>

          {submitted[idx] ? (
            <div className="w-full sm:w-24 flex items-center justify-center text-green-600">
              <CircleCheck className="h-5 w-5 text-green-500" />
            </div>
          ) : (
            <button
              type="button"
              onClick={() => handleSubmit(idx)}
              className="w-full sm:w-24 px-4 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center whitespace-nowrap disabled:opacity-50"
              disabled={!keys[idx] || loading[idx]}
            >
              {loading[idx] ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Submit"
              )}
            </button>
          )}
        </div>
      ))}
      <div className="space-y-6">* Please Click of Refresh Models After Adding the Keys to View the Models</div>
    </div>
  );
};

export default ApiKeysForm;
