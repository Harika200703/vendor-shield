import { useRef, useState } from "react";
import {
  UploadCloud,
  FileSpreadsheet,
  X,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ACCEPTED_FILES = [
  "vendors.csv",
  "transactions.csv",
  "vendor_changes.csv",
  "employees.csv",
];

function formatFileSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function getFileType(fileName) {
  const name = fileName.toLowerCase();

  if (name.includes("vendor_changes")) {
    return "Vendor Changes";
  }

  if (name.includes("transactions")) {
    return "Transactions";
  }

  if (name.includes("employees")) {
    return "Employees";
  }

  if (name.includes("vendors")) {
    return "Vendors";
  }

  return "CSV Dataset";
}

export default function UploadZone({
  files = [],
  onFilesChange,
  disabled = false,
}) {
  const inputRef = useRef(null);

  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState([]);

  function processFiles(fileList) {
    const incomingFiles = Array.from(fileList || []);

    const validFiles = [];
    const validationErrors = [];

    incomingFiles.forEach((file) => {
      const lowerName = file.name.toLowerCase();

      if (!lowerName.endsWith(".csv")) {
        validationErrors.push(
          `${file.name}: only CSV files are supported.`
        );

        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        validationErrors.push(
          `${file.name}: file exceeds the 10 MB limit.`
        );

        return;
      }

      const alreadyAdded = files.some(
        (existing) =>
          existing.name.toLowerCase() ===
          file.name.toLowerCase()
      );

      if (alreadyAdded) {
        validationErrors.push(
          `${file.name}: this file is already added.`
        );

        return;
      }

      validFiles.push({
        file,
        name: file.name,
        size: file.size,
        type: getFileType(file.name),
        status: "ready",
      });
    });

    setErrors(validationErrors);

    if (validFiles.length > 0) {
      onFilesChange([...files, ...validFiles]);
    }
  }

  function handleInputChange(event) {
    processFiles(event.target.files);

    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();

    setDragActive(false);

    if (disabled) {
      return;
    }

    processFiles(event.dataTransfer.files);
  }

  function removeFile(fileName) {
    const updated = files.filter(
      (item) => item.name !== fileName
    );

    onFilesChange(updated);

    setErrors((current) =>
      current.filter(
        (error) => !error.startsWith(fileName)
      )
    );
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDragEnter={(event) => {
          event.preventDefault();

          if (!disabled) {
            setDragActive(true);
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();

          if (!disabled) {
            setDragActive(true);
          }
        }}
        onDragLeave={(event) => {
          event.preventDefault();

          if (
            event.currentTarget === event.target
          ) {
            setDragActive(false);
          }
        }}
        onDrop={handleDrop}
        className={[
          "group relative overflow-hidden rounded-2xl border-2 border-dashed",
          "p-8 text-center transition-all duration-200",
          disabled
            ? "cursor-not-allowed border-slate-200 bg-slate-50 opacity-60"
            : dragActive
              ? "border-blue-500 bg-blue-50/70 shadow-lg shadow-blue-100"
              : "cursor-pointer border-slate-200 bg-slate-50/50 hover:border-blue-300 hover:bg-blue-50/30",
        ].join(" ")}
        onClick={() => {
          if (!disabled) {
            inputRef.current?.click();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          multiple
          className="hidden"
          onChange={handleInputChange}
          disabled={disabled}
        />

        <div
          className={[
            "mx-auto flex h-14 w-14 items-center justify-center rounded-2xl",
            "transition-transform duration-200",
            dragActive
              ? "scale-110 bg-blue-600 text-white"
              : "bg-blue-50 text-blue-600 group-hover:scale-105",
          ].join(" ")}
        >
          <UploadCloud size={27} strokeWidth={1.8} />
        </div>

        <h3 className="mt-5 text-sm font-bold text-slate-900">
          {dragActive
            ? "Drop your CSV files here"
            : "Upload your vendor data"}
        </h3>

        <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-slate-500">
          Drag and drop your CSV files here, or browse
          your computer. Vendor Shield will validate the
          files before analysis.
        </p>

        <button
          type="button"
          disabled={disabled}
          onClick={(event) => {
            event.stopPropagation();

            if (!disabled) {
              inputRef.current?.click();
            }
          }}
          className="mt-5 rounded-lg bg-slate-900 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Browse CSV Files
        </button>

        <div className="mt-4 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-[10px] text-slate-400">
          <span>CSV only</span>
          <span className="text-slate-300">•</span>
          <span>Maximum 10 MB per file</span>
          <span className="text-slate-300">•</span>
          <span>Multiple files supported</span>
        </div>
      </div>

      {/* Supported dataset types */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {ACCEPTED_FILES.map((fileName) => (
          <div
            key={fileName}
            className="flex items-center gap-2 rounded-lg border border-slate-100 bg-white px-3 py-2"
          >
            <FileSpreadsheet
              size={14}
              className="shrink-0 text-slate-400"
            />

            <span className="truncate text-[10px] font-medium text-slate-500">
              {fileName}
            </span>
          </div>
        ))}
      </div>

      {/* Validation errors */}
      {errors.length > 0 && (
        <div className="rounded-xl border border-red-100 bg-red-50 p-4">
          <div className="flex gap-3">
            <AlertCircle
              size={17}
              className="mt-0.5 shrink-0 text-red-500"
            />

            <div className="min-w-0">
              <p className="text-xs font-bold text-red-900">
                Upload validation
              </p>

              <div className="mt-2 space-y-1">
                {errors.map((error, index) => (
                  <p
                    key={`${error}-${index}`}
                    className="text-[11px] text-red-700"
                  >
                    {error}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Selected files */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold text-slate-700">
              Selected datasets
            </p>

            <span className="text-[10px] font-medium text-slate-400">
              {files.length} file
              {files.length !== 1 ? "s" : ""}
            </span>
          </div>

          {files.map((item) => (
            <div
              key={item.name}
              className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-50">
                <FileSpreadsheet
                  size={17}
                  className="text-emerald-600"
                />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate text-xs font-semibold text-slate-800">
                    {item.name}
                  </p>

                  <CheckCircle2
                    size={13}
                    className="shrink-0 text-emerald-500"
                  />
                </div>

                <div className="mt-0.5 flex items-center gap-2 text-[10px] text-slate-400">
                  <span>{item.type}</span>

                  <span>•</span>

                  <span>
                    {formatFileSize(item.size)}
                  </span>

                  <span>•</span>

                  <span className="text-emerald-600">
                    Ready for analysis
                  </span>
                </div>
              </div>

              <button
                type="button"
                onClick={() =>
                  removeFile(item.name)
                }
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-500"
                aria-label={`Remove ${item.name}`}
              >
                <X size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}