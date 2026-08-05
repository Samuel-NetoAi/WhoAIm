// Project ids are base64url-encoded "<creatureName>/<projectDirName>" pairs,
// so a Windows path with subdirectories can travel safely as a single URL
// path segment (app/api/projects/[projectId]/...).

export const encodeProjectId = (relativePath: string): string =>
  Buffer.from(relativePath.replace(/\\/g, "/"), "utf8").toString("base64url");

export const decodeProjectId = (id: string): string =>
  Buffer.from(id, "base64url").toString("utf8");
