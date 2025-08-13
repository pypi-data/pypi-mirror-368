CREATE_ASSET = """ 
mutation (
  $companyId: Int!,
  $name: String!,
  $scanType: AssetScan!
) {
  createAsset(
    input: {
      companyId: $companyId,
      name: $name,
      scanType: $scanType
    }
  ) {
    asset {
      id
      name
      createdAt
    }
    errors
  }
}
"""

UPDATE_ASSET = """
mutation (
  $id: ID!,
  $companyId: Int!,
  $name: String!,
  $tecnologyList: [String!],
  $repoUrl: String
) {
  updateAsset(
    input: {
      id: $id,
      companyId: $companyId,
      name: $name,
      tecnologyList: $tecnologyList,
      repoUrl: $repoUrl
    }
  ) {
    asset {
      id
    }
  }
}
"""

IMPORT_SBOM = """
mutation (
  $file: Upload!,
  $assetId: ID!,
  $companyId: ID!
) {
  importSbom(
    input: {
      file: $file,
      assetId: $assetId,
      companyId: $companyId
    }
  ) {
    success
  }
}
"""

IMPORT_CONTAINER = """
mutation (
  $file: Upload!,
  $assetId: ID!,
  $companyId: ID!
) {
  importContainerFindingsFile(
    input: {
      file: $file,
      assetId: $assetId,
      companyId: $companyId
    }
  ) {
    success
  }
}
"""

LOG_AST_ERROR = """
mutation (
  $companyId: ID!,
  $assetId: ID!,
  $log: String!
) {
  logAstError(
    input: {
      companyId: $companyId,
      assetId: $assetId,
      log: $log
    }
  ) {
    success
  }
}
"""

CREATE_DEPLOY = """
mutation (
  $assetId: ID!,
  $previousCommit: String!,
  $currentCommit: String!,
  $branchName: String,
  $diffContent: Upload!,
  $commitHistory: Upload!
) {
  createDeploy(
    input: {
      assetId: $assetId,
      previousCommit: $previousCommit,
      currentCommit: $currentCommit,
      branchName: $branchName,
      diffContent: $diffContent,
      commitHistory: $commitHistory
    }
  ) {
    deploy {
      id
    }
  }
}
"""

IMPORT_FINDINGS = """
mutation (
  $file: Upload!,
  $assetId: ID!,
  $companyId: ID!
  $vulnerabilityTypes: [Issue!]!
  $deployId: ID
  $commitRef: String
) {
  importAstFindingsFile(
    input: {
      file: $file,
      assetId: $assetId,
      companyId: $companyId,
      vulnerabilityTypes: $vulnerabilityTypes,
      deployId: $deployId,
      commitRef: $commitRef
    }
  ) {
    success
  }
}
"""
