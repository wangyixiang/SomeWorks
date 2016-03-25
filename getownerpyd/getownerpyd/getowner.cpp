#include <stdio.h>
#include <windows.h>
#include <tchar.h>
#include "accctrl.h"
#include "aclapi.h"
#include <strsafe.h>

#ifdef _DEBUG
#define _DEBUG_WAS_DEFINGED 1
#undef _DEBUG
#endif

#include <Python.h>

#ifdef _DEBUG_WAS_DEFINED
#define _DEBUG 1
#endif
static PyObject *GetOwnerError;

void SystemErrorMessage(LPTSTR lpszFunction)
{
	// Retrieve the system error message for the last-error code

	LPVOID lpMsgBuf;
	LPVOID lpDisplayBuf;
	DWORD dw = GetLastError();

	FormatMessage(
		FORMAT_MESSAGE_ALLOCATE_BUFFER |
		FORMAT_MESSAGE_FROM_SYSTEM |
		FORMAT_MESSAGE_IGNORE_INSERTS,
		NULL,
		dw,
		//MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		0x0409,
		(LPTSTR)&lpMsgBuf,
		0, NULL);

	// Display the error message and exit the process

	lpDisplayBuf = (LPVOID)LocalAlloc(LMEM_ZEROINIT,
		(lstrlen((LPCTSTR)lpMsgBuf) + lstrlen((LPCTSTR)lpszFunction) + 40) * sizeof(TCHAR));
	StringCchPrintf((LPTSTR)lpDisplayBuf,
		LocalSize(lpDisplayBuf) / sizeof(TCHAR),
		TEXT("%s failed with error %d: %s"),
		lpszFunction, dw, lpMsgBuf);
#ifdef _DEBUG
	_tprintf(TEXT("%s"), (LPTSTR)lpDisplayBuf);
#endif
	PyErr_SetString(GetOwnerError, (LPCTSTR)lpDisplayBuf);
	LocalFree(lpMsgBuf);
	LocalFree(lpDisplayBuf);
}

PyObject * GetOwner(LPCTSTR filename)
{
	DWORD dwRtnCode = 0;
	PSID pSidOwner = NULL;
	BOOL bRtnBool = TRUE;
	LPTSTR AcctName = NULL;
	LPTSTR DomainName = NULL;
	DWORD dwAcctName = 1, dwDomainName = 1;
	SID_NAME_USE eUse = SidTypeUnknown;
	HANDLE hFile;
	PSECURITY_DESCRIPTOR pSD = NULL;
	PyObject *result = NULL;


	// Get the handle of the file object.
	hFile = CreateFile(
		filename,
		GENERIC_READ,
		FILE_SHARE_READ,
		NULL,
		OPEN_EXISTING,
		// https://msdn.microsoft.com/en-us/library/aa363858(v=vs.85).aspx
		// You must set this flag to obtain a handle to a directory. A directory handle can be passed to some functions instead of a file handle.
		FILE_FLAG_BACKUP_SEMANTICS,
		NULL);

	// Check GetLastError for CreateFile error code.
	if (hFile == INVALID_HANDLE_VALUE) {
		DWORD dwErrorCode = 0;

		SystemErrorMessage(TEXT("CreateFile"));
		return NULL;
	}



	// Get the owner SID of the file.
	dwRtnCode = GetSecurityInfo(
		hFile,
		SE_FILE_OBJECT,
		OWNER_SECURITY_INFORMATION,
		&pSidOwner,
		NULL,
		NULL,
		NULL,
		&pSD);

	// Check GetLastError for GetSecurityInfo error condition.
	if (dwRtnCode != ERROR_SUCCESS) {
		DWORD dwErrorCode = 0;

		SystemErrorMessage(TEXT("GetSecurityInfo"));
		return NULL;
	}

	// First call to LookupAccountSid to get the buffer sizes.
	bRtnBool = LookupAccountSid(
		NULL,           // local computer
		pSidOwner,
		AcctName,
		(LPDWORD)&dwAcctName,
		DomainName,
		(LPDWORD)&dwDomainName,
		&eUse);

	// Reallocate memory for the buffers.
	AcctName = (LPTSTR)GlobalAlloc(
		GMEM_FIXED,
		dwAcctName*sizeof(TCHAR));

	// Check GetLastError for GlobalAlloc error condition.
	if (AcctName == NULL) {
		DWORD dwErrorCode = 0;

		SystemErrorMessage(TEXT("GlobalAlloc"));
		return NULL;
	}

	DomainName = (LPTSTR)GlobalAlloc(
		GMEM_FIXED,
		dwDomainName*sizeof(TCHAR));

	// Check GetLastError for GlobalAlloc error condition.
	if (DomainName == NULL) {
		DWORD dwErrorCode = 0;

		SystemErrorMessage(TEXT("GlobalAlloc"));
		GlobalFree(AcctName);
		return NULL;

	}

	// Second call to LookupAccountSid to get the account name.
	bRtnBool = LookupAccountSid(
		NULL,                   // name of local or remote computer
		pSidOwner,              // security identifier
		AcctName,               // account name buffer
		(LPDWORD)&dwAcctName,   // size of account name buffer 
		DomainName,             // domain name
		(LPDWORD)&dwDomainName, // size of domain name buffer
		&eUse);                 // SID type

								// Check GetLastError for LookupAccountSid error condition.
	if (bRtnBool == FALSE) {
		DWORD dwErrorCode = 0;

		dwErrorCode = GetLastError();

		if (dwErrorCode == ERROR_NONE_MAPPED)
			SystemErrorMessage(TEXT
				("Account owner not found for specified SID.\n"));
		else
			SystemErrorMessage(TEXT("LookupAccountSid"));
		GlobalFree(AcctName);
		GlobalFree(DomainName);
		return NULL;

	}
	else if (bRtnBool == TRUE)

		result = Py_BuildValue("ss", DomainName, AcctName);
		GlobalFree(AcctName);
		GlobalFree(DomainName);
		return result;
}


PyObject* getowner_function(PyObject* self, PyObject* args) {
	LPCTSTR filename;

	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;

	return GetOwner(filename);
}


PyMethodDef  GetownerMethods[] = {
	{ "getowner", (PyCFunction)getowner_function, METH_VARARGS, 0 },
	{ 0,0,0,0 }
};


PyMODINIT_FUNC
initgetowner(void)
{
	PyObject *m;

	m = Py_InitModule("getowner", GetownerMethods);
	if (m == NULL)
		return;

	GetOwnerError = PyErr_NewException("getowner.error", NULL, NULL);
	Py_XINCREF(GetOwnerError);
	PyModule_AddObject(m, "error", GetOwnerError);
}

